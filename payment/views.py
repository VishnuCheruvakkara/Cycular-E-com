from django.shortcuts import render,get_object_or_404,redirect
from cart.models import Cart
from user_side.models import Address
from orders.models import OrderAddress,Order,OrderItem
import re
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from wallet.models import Transaction
from coupon.models import Coupon,CouponUsage
import json
from django.http import JsonResponse
from decimal import Decimal
from django.utils import timezone
from datetime import datetime,time
from wallet.models import Wallet
from django.views.decorators.cache import never_cache
import razorpay

#####################  check out page  #################

def check_out(request):
    #retrive the current user's cart
  
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    #to take all address
    addresses=Address.objects.filter(user=request.user)
    #retrive all items for the current user cart
    cart_items=cart.items.all() #items is the related name
    total_price=sum(item.subtotal for item in cart_items)
    coupons = Coupon.objects.filter(active=True).order_by('-valid_until')
    
    # Fetch wallet for the current user
    wallet,created = Wallet.objects.get_or_create(user=request.user)
    wallet_balance = wallet.balance
   
    item_discount=0
    discount_value=0
    discount_amount=0
    coupon_code=None
    item_proportion=0
    coupon_grand_total=0
   
    # Calculate the total price of products
    total_price = sum(Decimal(item.subtotal) for item in cart_items)
  
    #get the data from the sessiion directly, that was stored with the help of javascript...
    applied_coupon=request.session.get('applied_coupon',None)
    if applied_coupon:
        # Access each value from the session
        coupon_code = applied_coupon.get('coupon_code')
        discount_value = applied_coupon.get('discount_value',0)
        valid_until = applied_coupon.get('valid_until')
        discount_amount = Decimal(applied_coupon.get('discount_amount', '0'))  # Convert from string to Decimal
        coupon_grand_total = Decimal(applied_coupon.get('coupon_grand_total', '0'))  # Convert from string to Decimal

    if total_price == 0:
        messages.info(request,'Your cart is empty.Please add products to the cart before proceeding to checkout.')
        return render(request, 'payment/check-out.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'addresses': addresses,
        })

    if request.method == 'POST':
        payment_method=request.POST.get('payment_method') 
        # Check if payment method is selected
        if not payment_method:
            messages.error(request, 'Please select a payment method before proceeding.')
            return render(request, 'payment/check-out.html', {
                'cart_items': cart_items,
                'total_price': total_price,
                'addresses': addresses,
                'coupons': coupons,
                'wallet_balance': wallet_balance,
            })
        # Check if any item in the cart exceeds ₹1000
        if total_price-discount_amount> 1000:
            if payment_method == 'cash_on_delivery':
                messages.error(request, 'Cash on delivery is not available for products priced above ₹1000.')
                return render(request, 'payment/check-out.html', {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'addresses': addresses,
                    'coupons':coupons,
                    'wallet_balance': wallet_balance,
                })
        try:
            #get address id
            address_id=request.POST.get('selected_address')

            # Check if an address was selected
            if not address_id:
                messages.error(request, 'Please select a delivery address before proceeding.')
                return render(request, 'payment/check-out.html', {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'addresses': addresses,
                    'coupons':coupons,
                    'wallet_balance': wallet_balance,      
                })
            selected_address=Address.objects.get(id=address_id)

            # Create a detailed description of items purchased
            item_descriptions = []
            for item in cart_items:
                item_descriptions.append(f"{item.product_variant.product.name}: {item.product_variant.size} (Qty: {item.quantity})")
            
            item_details = ', '.join(item_descriptions)

            # Calculate total price and wallet deduction
            total_price = sum(Decimal(item.subtotal) for item in cart_items)

            if coupon_grand_total != 0 :
                val=coupon_grand_total
            else:
                val=total_price
            # Handle wallet payment
            if payment_method == 'wallet':
                if wallet_balance < val:
                    messages.error(request, f'Insufficient wallet balance to complete the purchase. Current balance is: {wallet_balance} ₹. Choose any other payment option.')
                    return render(request, 'payment/check-out.html', {
                        'cart_items': cart_items,
                        'total_price': total_price,
                        'addresses': addresses,
                        'coupons':coupons,
                        'wallet_balance': wallet_balance,
                    })
                
                # Deduct wallet balance only after confirmation
                wallet.balance -=  val
                wallet.save()

                # Create a new Transaction entry for the wallet
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='debit',
                    transaction_purpose='purchase',
                    transaction_amount = val,
                    description=f"Wallet payment for order : {item_details}"
                )

            order=Order.objects.create(
                user=request.user,
                payment_method=payment_method,
                total_price=total_price,
                coupon_discount_total=discount_amount,
            )

            #save the address to the table 
            order_address=OrderAddress.objects.create(
                order=order,
                address_line=selected_address.address_line,
                city=selected_address.city,
                state=selected_address.state,
                country=selected_address.country,
                postal_code=selected_address.postal_code,
                phone_number=selected_address.phone_number,
            )
            for item in cart_items:
                item_subtotal = Decimal(item.subtotal)
                total_price_decimal = Decimal(total_price) 

                item_proportion = (item_subtotal / total_price_decimal)
                item_discount = ((item_proportion)* discount_amount)
               
                # to decreace stock count of product when user buy it
                product_variant = item.product_variant
                if product_variant.stock >= item.quantity:
                    product_variant.stock -= item.quantity
                    product_variant.save()  # Save the updated stock count
                else:
                    messages.error(request, f"Not enough stock for {product_variant.product.name}.")
                    return redirect('cart:cart-view')  # Redirect if stock is insufficient
                order_item=OrderItem.objects.create(
                    order=order,
                    product_variant=item.product_variant,
                    quantity=item.quantity,
                    price=item.subtotal,
                    coupon_discount_price=item_discount,
                    coupon_info=f"{discount_value}% of {coupon_code} coupon applied.Discount of {item_discount:.2f} ₹"
                )
            
            # check whether user select the razorpay for payment
            if payment_method == 'razorpay':
                return redirect(reverse('payment:razorpay-order', args=[order.id]))
           
            # Clear the cart after successful purchase
            cart.items.all().delete()
            if 'applied_coupon' in request.session:
                # Get the coupon object
                coupon = Coupon.objects.get(code=applied_coupon['coupon_code'])
                # Fetch or create the CouponUsage instance for the user
                coupon_usage, created = CouponUsage.objects.get_or_create(user=request.user, coupon=coupon)
                # Mark the coupon as used
                coupon_usage.is_used = True
                coupon_usage.save()
                del request.session['applied_coupon']
            
            messages.success(request,'Order was placed successfully. Details are added to the order-history...')
            return redirect(reverse('payment:order-success-page',args=[order.id]))
        except Exception as e:
            messages.error(request, 'An error occurred while placing the order.')
   
    context={
        'cart_items':cart_items,
        'total_price':total_price,
        'addresses':addresses,
        'coupons':coupons,
        'wallet_balance': wallet_balance,
    }

    return render(request,'payment/check-out.html',context)

############################  add address in check out page.  ###################

def add_address_checkout(request):

    errors = {}  # Dictionary to hold error messages

    # Fetch all addresses of the logged-in user
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        address_line = request.POST.get('address_line', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        is_default = request.POST.get('is_default') == 'on'

        # Validation for Address Line
        if not address_line:
            errors['address_line'] = 'Address line is required.'
        elif len(address_line) < 5 or len(address_line) > 100:
            errors['address_line'] = 'Address line must be between 5 and 100 characters.'
        elif re.search(r'[^a-zA-Z0-9\s,.-]', address_line):
            errors['address_line'] = 'Address line contains invalid characters.'

        # Validation for City
        if not city:
            errors['city'] = 'City is required.'
        elif len(city) > 50:
            errors['city'] = 'City name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', city):
            errors['city'] = 'City must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in city):
            errors['city'] = 'City name cannot contain numbers.'

        # Validation for State
        if not state:
            errors['state'] = 'State is required.'
        elif len(state) > 50:
            errors['state'] = 'State name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', state):
            errors['state'] = 'State must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in state):
            errors['state'] = 'State name cannot contain numbers.'

        # Validation for Country
        if not country:
            errors['country'] = 'Country is required.'
        elif len(country) > 50:
            errors['country'] = 'Country name is too long (max 50 characters).'
        elif not re.match(r'^[a-zA-Z\s\-]+$', country):
            errors['country'] = 'Country must only contain letters, spaces, or hyphens.'
        elif any(char.isdigit() for char in country):
            errors['country'] = 'Country name cannot contain numbers.'

        # Validation for Postal Code
        if not postal_code:
            errors['postal_code'] = 'Postal code is required.'
        elif not re.match(r'^\d{4,10}$', postal_code):
            errors['postal_code'] = 'Postal code must be between 4 and 10 digits and contain only numbers.'
        elif len(postal_code) > 10:
            errors['postal_code'] = 'Postal code is too long (max 10 digits).'

        # Validation for Phone Number with Mandatory Country Code
        if not phone_number:
            errors['phone_number'] = 'Phone number is required.'
        elif not re.match(r'^\+\d{1,4}\d{6,10}$', phone_number):
            errors['phone_number'] = (
                'Phone number must start with a "+" followed by 1-4 digits for the country code '
                'and then 6-10 digits for the phone number itself.'
            )
        elif phone_number[0] != '+':
            errors['phone_number'] = 'Phone number must start with a "+" followed by the country code.'

        # If no errors, create the address
        if not errors:
            Address.objects.create(
                user=request.user,
                address_line=address_line,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code,
                phone_number=phone_number,
                is_default=is_default
            )
            messages.success(request, 'Address added successfully.')
            return redirect('payment:check-out')
        else:
           
            messages.error(request, 'Please correct the errors in Add address form.')

    context = {
        'errors': errors,
        'addresses':addresses,
    }

    return render(request, 'payment/check-out.html', context)

###################  order success page  ###########################

def order_success_page(request,order_id):
    # Fetch the order using the order_id
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items=order.items.all()
   
    order_address = getattr(order, 'order_address', None)     

    # Pass order and address details to the template
    context = {
        'order': order,
        'order_address': order_address,
    }
    return render(request,'payment/order-success-page.html',context)

##################### Razor pay payment views logic  ###########################

@never_cache
def create_razorpay_order(request, order_id):
 
    order = get_object_or_404(Order, id=order_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

    payment_amount = int(order.paid_amount() * 100)  # Convert to paisa
    payment_currency = 'INR'

    razorpay_order = client.order.create({
        'amount': payment_amount,
        'currency': payment_currency,
        'payment_capture': '1'  # Auto-capture payment
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()
  
    context = {
        'razorpay_key_id': settings.RAZORPAY_API_KEY,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_amount': payment_amount,
        'order_id': order.id,
    }
    return render(request, 'payment/razorpay_payment.html', context)

###################  payment success page by razor pay  #####################

def payment_success(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    order_items=order.items.all()
    #retrive the current user's cart
    cart=get_object_or_404(Cart,user=request.user)
    
    # Verify the payment 
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    try:
        payment = client.payment.fetch(razorpay_payment_id)
        if payment['status'] == 'captured':
            order.order_status = 'Order placed'
            order.save()
            # Clear the cart only if the payment is successful
            cart.items.all().delete()

            # Handle coupon usage if applied
            applied_coupon = request.session.get('applied_coupon', None)
            if applied_coupon:
                coupon = Coupon.objects.get(code=applied_coupon['coupon_code'])
                coupon_usage, created = CouponUsage.objects.get_or_create(user=request.user, coupon=coupon)
                coupon_usage.is_used = True
                coupon_usage.save()

                # Remove the coupon from the session
                del request.session['applied_coupon']

            wallet = request.user.wallet
            for order_item in order_items:
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='null',
                    transaction_purpose='purchase',
                    transaction_amount=order_item.effective_price(),
                    description=f"{order_item.product_variant.product.name} Purchase via Razorpay"
                )
            
            messages.success(request, 'Payment successful and order placed successfully!')
        else:
            messages.error(request, 'Payment failed.')
    except Exception as e:
        messages.error(request, 'An error occurred while verifying the payment.')

    return render(request, 'payment/razorpay-success-page.html', {'order': order})

####################### payment-cancell  ############################

def payment_cancel(request):
    # Get the order ID from the request
    order_id = request.GET.get('order_id')

    # Retrieve the order using the order ID
    order = get_object_or_404(Order, id=order_id)
    cart=get_object_or_404(Cart,user=request.user)

    # Update the order status to 'Cancelled'
    order.order_status = 'Payment Failed'
    order.save()
    cart.items.all().delete()
    # Handle coupon usage if applied
    applied_coupon = request.session.get('applied_coupon', None)
    if applied_coupon:
        coupon = Coupon.objects.get(code=applied_coupon['coupon_code'])
        coupon_usage, created = CouponUsage.objects.get_or_create(user=request.user, coupon=coupon)
        coupon_usage.is_used = True
        coupon_usage.save()

        # Remove the coupon from the session
        del request.session['applied_coupon']

    # Provide feedback to the user
    messages.warning(request, 'Your payment has been failed.Try to complete payment from the order history page.')

    # Render the cancellation template with order details
    return render(request, 'payment/razorpay-cancell-page.html', {'order': order})

####################### apply coupon logic  #######################

def apply_coupon_view(request):

    if request.method == "POST":
        data=json.loads(request.body)
        coupon_code=data.get('coupon_code')
        #get the total price...
        cart=get_object_or_404(Cart,user=request.user)
        cart_items=cart.items.all()
        total_price=sum(item.subtotal for item in cart_items)
        # Check if the cart is empty
        if total_price == 0:
            return JsonResponse({'error': 'Your cart is empty. Please add products to the cart to apply a coupon.'}, status=400)
        try:
            coupon = Coupon.objects.get(code=coupon_code,active=True)
            # Ensure the expiration time is 12:00 PM on the valid_until date
            expiration_time = timezone.make_aware(
                datetime.combine(coupon.valid_until.date(), time(12, 0))
            )

            # Check if the coupon is expired (after 12:00 PM on the expiration date)
            if timezone.now() > expiration_time:
                return JsonResponse({'error': 'This coupon has expired.'}, status=400)
            
            # Check if the user has already used the coupon
            coupon_usage, created = CouponUsage.objects.get_or_create(user=request.user, coupon=coupon)
            if coupon_usage.is_used:
                return JsonResponse({'error': 'You have already used this coupon.'}, status=400)

            # Check if the total price is less than ₹3000
            if total_price < 3000:
                return JsonResponse({ 'error': 'Coupon are applicable for the product price less than 3000 ₹'}, status=400)
            
            total_price_decimal = Decimal(total_price)
            discount_amount=((Decimal(coupon.discount_value)) / 100) * total_price_decimal
            valid_until_str = coupon.valid_until.strftime('%B %d, %Y')
            coupon_grand_total=total_price_decimal-discount_amount
            # Store the coupon details in the session
            # Check if the discount results in a grand total less than ₹3000 after applying the coupon
            if coupon_grand_total < 3000:
                return JsonResponse({
                    'error': f'Coupon : "{coupon.code}" is not applicable for this product, Try any other Coupon less than {coupon.discount_value}%.'}, status=400)
            discount_amount_float = float(discount_amount)
            coupon_grand_total_float = float(coupon_grand_total)
            
            request.session['applied_coupon'] = {
                'coupon_code': coupon.code,
                'discount_value': coupon.discount_value,
                'valid_until': valid_until_str,
                'discount_amount': str(discount_amount_float),  # Convert to str for consistent formatting
                'coupon_grand_total': str(coupon_grand_total_float),  # Convert to str for consistent formatting
            }
          
            return JsonResponse({
                'message': f'Coupon applied! You saved {discount_amount:.2f} ₹',
                'coupon_code': coupon.code,
                'discount_value': coupon.discount_value,
                'valid_until': valid_until_str,
                'coupon_grand_total':f'{coupon_grand_total:.2f}',
                'discount_amount':f'-{discount_amount:.2f}',
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'error': 'Invalid or inactive coupon code, Check the available coupon'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)