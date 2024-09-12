from django.shortcuts import render,get_object_or_404,redirect
from cart.models import Cart,CartItem
from user_side.models import Address
from orders.models import OrderAddress,Order,OrderItem
import re
from django.contrib import messages
from django.urls import reverse
from django.conf import settings


                      
import razorpay


# Create your views here.
#####################  check out page  #################

def check_out(request):
    #retrive the current user's cart
    cart=get_object_or_404(Cart,user=request.user)
    #to take all address
    addresses=Address.objects.filter(user=request.user)
    #retrive all items for the current user cart
    cart_items=cart.items.all() #items is the related name
    
    #total price of product
    total_price=sum(item.subtotal for item in cart_items)
    
    if total_price == 0 :
        messages.info(request,'Your cart is empty.Please add products to the cart before proceeding to checkout.')
        return render(request, 'payment/check-out.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'addresses': addresses,
        })

    if request.method == 'POST':
        payment_method=request.POST.get('payment_method') 
        try:
            #get address id
            address_id=request.POST.get('selected_address')
            selected_address=Address.objects.get(id=address_id)
            
           
            order=Order.objects.create(
                user=request.user,
                payment_method=payment_method,
                total_price=total_price,
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
                product_variant = item.product_variant
                if product_variant.stock >= item.quantity:
                    product_variant.stock -= item.quantity
                    product_variant.save()  # Save the updated stock count
                else:
                    messages.error(request, f"Not enough stock for {product_variant.product.name}.")
                    return redirect('cart:cart-view')  # Redirect if stock is insufficient
                OrderItem.objects.create(
                    order=order,
                    product_variant=item.product_variant,
                    quantity=item.quantity,
                    price=item.subtotal,
                )

            #check whether user select the razorpay for payment
            if payment_method == 'razorpay':
                return redirect(reverse('payment:razorpay-order', args=[order.id]))
            
            # Clear the cart after successful purchase
            cart.items.all().delete()

            
            messages.success(request,'Order was placed successfully. Check out order History page to track order status...')
            return redirect(reverse('payment:order-success-page',args=[order.id]))
        except Exception as e:
            # Log the exception
            print(f"Error: {e}")
            messages.error(request, 'An error occurred while placing the order.')
  
    context={
        'cart_items':cart_items,
        'total_price':total_price,
        'addresses':addresses,
    }
    return render(request,'payment/check-out.html',context)

############################  add address in check out page.  ###################

def add_address_checkout(request):

    print("add address check out works")

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

    # Optionally, you might want to get the address details as well
    order_address = getattr(order, 'order_address', None)

    # Pass order and address details to the template
    context = {
        'order': order,
        'order_address': order_address,
    }
    return render(request,'payment/order-success-page.html',context)


##################### Razor pay payment views logic  ###########################

# views.py

def create_razorpay_order(request, order_id):
 
    order = get_object_or_404(Order, id=order_id)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))

    payment_amount = int(order.total_price * 100)  # Convert to paisa
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
    #retrive the current user's cart
    cart=get_object_or_404(Cart,user=request.user)
    
    # Verify the payment (optional but recommended)
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    try:
        payment = client.payment.fetch(razorpay_payment_id)
        if payment['status'] == 'captured':
            order.order_status = 'Delivered'
            order.save()
            # Clear the cart only if the payment is successful
            cart.items.all().delete()
            
            messages.success(request, 'Payment successful and order placed successfully!')
        else:
            messages.error(request, 'Payment failed.')
    except Exception as e:
        messages.error(request, 'An error occurred while verifying the payment.')

    return render(request, 'payment/razorpay-success-page.html', {'order': order})

###############################
