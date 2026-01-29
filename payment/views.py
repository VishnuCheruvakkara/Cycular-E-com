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
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_POST
from user_side.validation import validate_address_data
from django.contrib.messages import get_messages
from django.views.decorators.csrf import csrf_exempt
import uuid

#####################  check out page  #################

def get_checkout_context(request, errors=None,form_data=None):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()
    total_price = sum(Decimal(item.subtotal) for item in cart_items)
    addresses = Address.objects.filter(user=user)
    coupons = Coupon.objects.filter(active=True).order_by('-valid_until')
    used_coupon_ids = CouponUsage.objects.filter(user=user, is_used=True).values_list('coupon_id', flat=True)
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet_balance = wallet.balance
    applied_coupon = request.session.get('applied_coupon')

    discount_amount = Decimal(applied_coupon.get('discount_amount', '0')) if applied_coupon else Decimal('0')
    coupon_grand_total = Decimal(applied_coupon.get('coupon_grand_total', '0')) if applied_coupon else Decimal('0')
    coupon_code = applied_coupon.get('coupon_code') if applied_coupon else None
    discount_value = applied_coupon.get('discount_value', 0) if applied_coupon else 0

    context = {
        'errors': errors or {},
        'form_data': form_data or {},
        'addresses': addresses,
        'cart_items': cart_items,
        'total_price': total_price,
        'coupons': coupons,
        'wallet_balance': wallet_balance,
        'used_coupon_ids': used_coupon_ids,
        'applied_coupon': applied_coupon,
        'discount_amount': discount_amount,
        'coupon_grand_total': coupon_grand_total,
        'coupon_code': coupon_code,
        'discount_value': discount_value,
    }
    return context

@login_required(login_url='user_side:sign-in')
def check_out(request):
    context = get_checkout_context(request)

    # Empty cart check
    if context['total_price'] == 0:
        messages.info(
            request,
            'Your cart is empty or this checkout session is no longer valid.'
        )
        return render(request, 'payment/checkout_blocked.html')
    
    if request.method == 'POST':
    
        payment_method = request.POST.get('payment_method')

        if not payment_method:
            messages.error(request, 'Please select a payment method before proceeding.')
            return render(request, 'payment/check-out.html', context)

        # COD limit check
        if (
            context['total_price'] - context['discount_amount'] > 1000
            and payment_method == 'cash_on_delivery'
        ):
            messages.error(
                request,
                'Cash on delivery is not available for products priced above ₹1000.'
            )
            return render(request, 'payment/check-out.html', context)

        try:
            address_id = request.POST.get('selected_address')
            if not address_id:
                messages.error(request, 'Please select a delivery address before proceeding.')
                return render(request, 'payment/check-out.html', context)

            selected_address = get_object_or_404(
                Address,
                id=address_id,
                user=request.user
            )

            total_price = sum(Decimal(item.subtotal) for item in context['cart_items'])
            val = context['coupon_grand_total'] if context['coupon_grand_total'] != 0 else total_price

            item_descriptions = [
                f"{item.product_variant.product.name}: "
                f"{item.product_variant.size} (Qty: {item.quantity})"
                for item in context['cart_items']
            ]
            item_details = ', '.join(item_descriptions)

            # Wallet balance check BEFORE atomic
            if payment_method == 'wallet' and context['wallet_balance'] < val:
                messages.error(
                    request,
                    f'Insufficient wallet balance. Current balance: {context["wallet_balance"]} ₹'
                )
                return render(request, 'payment/check-out.html', context)

            # ATOMIC BLOCK 
            with transaction.atomic():
                
                order_status = 'Pending Payment' if payment_method == 'razorpay' else 'Order placed'

                order = Order.objects.create(
                    user=request.user,
                    payment_method=payment_method,
                    total_price=total_price,
                    coupon_discount_total=context['discount_amount'],
                    order_status=order_status,
                )

                OrderAddress.objects.create(
                    order=order,
                    address_line=selected_address.address_line,
                    city=selected_address.city,
                    state=selected_address.state,
                    country=selected_address.country,
                    postal_code=selected_address.postal_code,
                    phone_number=selected_address.phone_number,
                )

                # Create order items once
               
                for item in context['cart_items']:
                    product_variant = item.product_variant

                    if product_variant.stock < item.quantity:
                        raise ValueError(
                            f"{product_variant.product.name} is out of stock "
                            f"({product_variant.stock} left)"
                        )
                    if payment_method in ['wallet', 'cash_on_delivery']:
                        product_variant.stock -= item.quantity
                        product_variant.save()

                    # Reduce stock immediately for Wallet / COD
                    item_subtotal = Decimal(item.subtotal)
                    item_discount = (
                        (item_subtotal / Decimal(total_price))
                        * context['discount_amount']
                    ) if total_price else Decimal('0')

                    item_status = ( 'Pending Payment' if payment_method == 'razorpay' else 'Order placed' )

                    OrderItem.objects.create(
                        order=order,
                        product_variant=product_variant,
                        quantity=item.quantity,
                        price=item.subtotal,
                        coupon_discount_price=item_discount,
                        coupon_info=(
                            f"{context['discount_value']}% of "
                            f"{context['coupon_code']} coupon applied. "
                            f"Discount {item_discount:.2f} ₹"
                        ),
                        order_item_status = item_status
                    )

                # Wallet payment
                if payment_method == 'wallet':
                    wallet = Wallet.objects.select_for_update().get(user=request.user)
                    wallet.balance -= val
                    wallet.save()

                    Transaction.objects.create(
                        wallet=wallet,
                        transaction_type='debit',
                        transaction_purpose='purchase',
                        transaction_amount=val,
                        description=f"Wallet payment for order : {item_details}"
                    )

            # END ATOMIC 

            # Razorpay redirect 
            if payment_method == 'razorpay':
                cart = Cart.objects.get(user=request.user)
                cart.items.all().delete()

                return redirect(
                    reverse('payment:razorpay-order', args=[order.id])
                )

            # Clear cart ONLY for wallet / COD
            if payment_method in ['wallet', 'cash_on_delivery']:
                order.order_status = 'Order placed'
                order.save()

                cart = Cart.objects.get(user=request.user)
                cart.items.all().delete()

                if 'applied_coupon' in request.session:
                    coupon = Coupon.objects.get(
                        code=request.session['applied_coupon']['coupon_code']
                    )
                    coupon_usage, _ = CouponUsage.objects.get_or_create(
                        user=request.user,
                        coupon=coupon
                    )
                    coupon_usage.is_used = True
                    coupon_usage.save()
                    del request.session['applied_coupon']

            messages.success(
                request,
                'Order was placed successfully. Details are added to order history.'
            )
            return redirect(
                reverse('payment:order-success-page', args=[order.id])
            )

        except Exception as e:
            print(e)
            messages.error(
                request,
                'An error occurred while placing the order.'
            )
            return render(request, 'payment/check-out.html', context)

    return render(request, 'payment/check-out.html', context)

###################  Add address ####################

@login_required(login_url='user_side:sign-in')
def add_address_checkout(request):
    errors = {}
    form_data = {}
    
    if request.method == 'POST':
        errors, form_data = validate_address_data(request.POST)

        if not errors:
            Address.objects.create(user=request.user, **form_data)
            messages.success(request, 'Address added successfully.')
            return redirect('payment:check-out')
        else:
            messages.error(request, 'Please correct the errors in Add address form.')
           
    context = get_checkout_context(request, errors=errors,form_data=form_data)
    return render(request, 'payment/check-out.html', context)


###################  order success page  ###########################

@login_required(login_url='user_side:sign-in')
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

##################### Razor pay payment views logic per orders  ###########################

@login_required(login_url='user_side:sign-in')
@never_cache
def create_razorpay_order(request, order_id):

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.order_status == 'Order placed':
        messages.info(request, 'This order is already paid.')
        return redirect('payment:order-success-page', order.id)

    if order.is_razorpay_in_progress and order.razorpay_order_id:
        messages.info(
            request,
            'Payment is already in progress. Please complete it.'
        )
        return render(request, 'payment/razorpay_payment.html', {
            'order': order,
            'order_item': None,
            'razorpay_key_id': settings.RAZORPAY_API_KEY,
            'razorpay_order_id': order.razorpay_order_id,
            'razorpay_amount': int(order.paid_amount() * 100),
            'order_id': order.id,
        })

    with transaction.atomic():
        order = Order.objects.select_for_update().get(id=order.id)

        if order.is_razorpay_in_progress:
            return render(request, 'payment/razorpay_payment.html', {
                'order': order,
                'order_item': None,
                'razorpay_key_id': settings.RAZORPAY_API_KEY,
                'razorpay_order_id': order.razorpay_order_id,
                'razorpay_amount': int(order.paid_amount() * 100),
                'order_id': order.id,
            })

        order.is_razorpay_in_progress = True
        order.save()

    client = razorpay.Client(
        auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY)
    )

    payment_amount = int(order.paid_amount() * 100)

    razorpay_order = client.order.create({
        'amount': payment_amount,
        'currency': 'INR',
        'payment_capture': 1
    })

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    return render(request, 'payment/razorpay_payment.html', {
        'order': order,
        'order_item': None,
        'razorpay_key_id': settings.RAZORPAY_API_KEY,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_amount': payment_amount,
        'order_id': order.id,
    })

################## Verify Razor pay payment ###########################

@login_required
def verify_razorpay_payment(request):
    data = json.loads(request.body)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_API_KEY,
        settings.RAZORPAY_API_SECRET_KEY
    ))

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature'],
        })

        order = get_object_or_404(
            Order,
            razorpay_order_id=data['razorpay_order_id'],
            user=request.user
        )
        
        payment = client.payment.fetch(data['razorpay_payment_id'])

        if payment['order_id'] != data['razorpay_order_id']:
            return JsonResponse({'status': 'order_mismatch'})
        
        expected_amount = int(order.paid_amount() * 100)

        if payment['amount'] != expected_amount:
            return JsonResponse({'status': 'amount_mismatch'})

        if payment['status'] != 'captured':
            return JsonResponse({'status': 'failed'})
        
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'status': 'failed'})

    try:
        with transaction.atomic():

            order = Order.objects.select_for_update().get(
                razorpay_order_id=data['razorpay_order_id'],
                user=request.user
            )


            # BLOCK DOUBLE PAYMENT
            if order.razorpay_payment_id:
                return JsonResponse({'status': 'already_paid'})

            order_items = order.items.all()

            # REDUCE STOCK
            for order_item in order_items:
                pv = order_item.product_variant
                if pv.stock < order_item.quantity:
                    return JsonResponse({'status': 'out_of_stock'})
                pv.stock -= order_item.quantity
                pv.save()

            for item in order_items:
                item.order_item_status = 'Order placed'
                item.save(update_fields=['order_item_status'])

            # LOCK ORDER
            order.razorpay_payment_id = data['razorpay_payment_id']
            order.order_status = 'Order placed'
            order.is_razorpay_in_progress = False
            order.save()

            # HANDLE COUPON
            applied_coupon = request.session.get('applied_coupon')
            if applied_coupon:
                coupon = Coupon.objects.get(code=applied_coupon['coupon_code'])
                usage, _ = CouponUsage.objects.get_or_create(
                    user=request.user,
                    coupon=coupon
                )
                usage.is_used = True
                usage.save()
                del request.session['applied_coupon']

            # WALLET TRANSACTION LOG
            wallet = request.user.wallet
            for item in order_items:
                Transaction.objects.create(
                    wallet=wallet,
                    transaction_type='null',
                    transaction_purpose='purchase',
                    transaction_amount=item.effective_price(),
                    description=f"{item.product_variant.product.name} Purchase via Razorpay"
                )
            

    except Exception:
        return JsonResponse({'status': 'error'})

    return JsonResponse({
        'status': 'success',
        'redirect_url': reverse('payment:order-success-page', args=[order.id])
    })

###################  payment success page by razor pay  #####################


@login_required(login_url='user_side:sign-in')
def payment_success(request):
    order_id = request.GET.get('order_id')

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'payment/razorpay-success-page.html',
        {'order': order}
    )


####################### payment-cancell for entire order  ############################

@login_required(login_url='user_side:sign-in')
def payment_cancel(request):
    # Get the order ID from the request
    order_id = request.GET.get('order_id')

    # Retrieve the order using the order ID
    order = get_object_or_404(Order, id=order_id,user=request.user)

    # Clear old messages
    storage = get_messages(request)
    for _ in storage:
        pass

    with transaction.atomic():
        order.order_status = 'Payment Failed'
        order.is_razorpay_in_progress = False
        order.save(update_fields=['order_status', 'is_razorpay_in_progress'])
        
        order.items.update(
            order_item_status='Payment Failed',
            is_razorpay_in_progress=False
        )

    
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
    messages.info(request, 'Your payment has been failed.Try to complete payment from the order history page.')

    # Render the cancellation template with order details
    return render(request, 'payment/razorpay-cancell-page.html', {'order': order,'is_item_payment': False})

####################### apply coupon logic  #######################

@login_required(login_url='user_side:sign-in')
def apply_coupon_view(request):

    if request.method == "POST":
        data = json.loads(request.body)
        coupon_code = data.get('coupon_code')

        # Get cart & total
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        total_price = sum(Decimal(item.subtotal) for item in cart_items)

        # Empty cart check
        if total_price == 0:
            return JsonResponse({
                'error': 'Your cart is empty. Please add products to the cart to apply a coupon.'
            }, status=400)

        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)

            # Expiry check (end of day)
            expiration_time = timezone.make_aware(
                datetime.combine(coupon.valid_until.date(), time(23, 59, 59))
            )
            if timezone.now() > expiration_time:
                return JsonResponse({'error': 'This coupon has expired.'}, status=400)

            # Already used check
            coupon_usage, _ = CouponUsage.objects.get_or_create(
                user=request.user,
                coupon=coupon
            )
            if coupon_usage.is_used:
                return JsonResponse({
                    'error': 'You have already used this coupon.'
                }, status=400)

            # Min purchase check (NO hard coding)
            if total_price < coupon.min_purchase_amount:
                return JsonResponse({
                    'error': f'Coupon valid only for orders above ₹{coupon.min_purchase_amount}'
                }, status=400)

            # Calculate discount
            discount_amount = (
                Decimal(coupon.discount_value) / 100
            ) * total_price

            # Max discount cap
            if coupon.max_discount_amount:
                discount_amount = min(
                    discount_amount,
                    Decimal(coupon.max_discount_amount)
                )

            coupon_grand_total = total_price - discount_amount

            # Safety check (should not go negative)
            if coupon_grand_total <= 0:
                return JsonResponse({
                    'error': 'Invalid discount amount.'
                }, status=400)

            valid_until_str = coupon.valid_until.strftime('%B %d, %Y')

            # Store in session
            request.session['applied_coupon'] = {
                'coupon_code': coupon.code,
                'discount_value': coupon.discount_value,
                'valid_until': valid_until_str,
                'discount_amount': str(discount_amount),
                'coupon_grand_total': str(coupon_grand_total),
            }

            return JsonResponse({
                'message': f'Coupon applied! You saved {discount_amount:.2f} ₹',
                'coupon_code': coupon.code,
                'discount_value': coupon.discount_value,
                'valid_until': valid_until_str,
                'coupon_grand_total': f'{coupon_grand_total:.2f}',
                'discount_amount': f'-{discount_amount:.2f}',
            })

        except Coupon.DoesNotExist:
            return JsonResponse({
                'error': 'Invalid or inactive coupon code. Check available coupons.'
            }, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

######################### Cancell coupon logic #########################

@login_required(login_url='user_side:sign-in')
def remove_coupon_view(request):
    if request.method == "POST":
        if 'applied_coupon' in request.session:
            del request.session['applied_coupon']

        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.items.all()
        total_price = sum(Decimal(item.subtotal) for item in cart_items)

        return JsonResponse({
            'message': 'Coupon removed successfully',
            'total_price': f'{total_price:.2f}',
            'discount_amount': '0.00'
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
