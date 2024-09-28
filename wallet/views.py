from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Wallet, Transaction
from orders.models import OrderItem
from django.http import JsonResponse
from decimal import Decimal
import json
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.utils import timezone
# Create your views here.



#######################  wallet-page  ###################


def wallet_page(request):
 
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    transactions = wallet.transactions.all().order_by('-created_at')

   
    context = {
        "wallet": wallet,
        "transactions": transactions,
    }
    return render(request, 'wallet/wallet-page.html', context)


##########################  orderitem cacelling logic   ####################

def cancell_order_item(request, order_item_id):
    # Ensure it's a POST request for safety
    if request.method == 'POST':

        data = json.loads(request.body)
        captcha_response = data.get('captcha_response')
        captcha_key = data.get('captcha_key')
        # Debugging information
        print(f"Received CAPTCHA key: {captcha_key}")
        print(f"Received CAPTCHA response: {captcha_response}")

        # Validate CAPTCHA
        try:
            # Query by hashkey (adjust according to your CaptchaStore model)
            captcha_store = CaptchaStore.objects.get(hashkey=captcha_key)
            
            # Debugging information
            print(f"Stored CAPTCHA response: {captcha_store.response}")
            
            # Validate the response
            if captcha_store.response.upper() != captcha_response:
                return JsonResponse({'error': 'Invalid CAPTCHA response'}, status=400)
        
        except CaptchaStore.DoesNotExist:
            return JsonResponse({'error': 'CAPTCHA key not found'}, status=400)




        # Get the order item to be cancelled
        order_item = get_object_or_404(OrderItem, id=order_item_id)

        # Check if the status is already "Cancelled" (optional for extra safety)
        if order_item.order_item_status == 'Cancelled':
            return JsonResponse({'error': 'Order item is already cancelled.'}, status=400)

        # Update the order item status to "Cancelled"
        order_item.order_item_status = 'Cancelled'
        order_item.cancelled_message = f"Order cancelled by User : {request.user.username} on {timezone.now().strftime('%d %b %Y, %I:%M %p')}" 
        order_item.save()

        # Update the stock of the product variant by the order item quantity
        product_variant = order_item.product_variant
        product_variant.stock += order_item.quantity
        product_variant.save()

        # Fetch or create the user's wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        # Add the order item price to the wallet balance
        wallet.balance += Decimal(order_item.price)
     
        wallet.save()

        # Log the transaction
        Transaction.objects.create(
            wallet=wallet,
            transaction_type='credit',
            transaction_purpose='refund',
            transaction_amount=Decimal(order_item.price),
            description=f"{order_item.product_variant.product.name} was cancelled",
        )

        # Send a success response indicating the cancellation and wallet refund
        return JsonResponse({'message': 'Order item has been cancelled and amount added to your wallet.'})

    # If not a POST request, return a bad request response
    return JsonResponse({'error': 'Invalid request method.'}, status=400)




def captcha_image_view(request):
    new_key = CaptchaStore.generate_key()  # Generate a unique CAPTCHA key
    image_url = captcha_image_url(new_key)  # Get the image URL for the generated key
    
    # Return both the CAPTCHA key and URL as JSON
    return JsonResponse({
        'captcha_key': new_key,
        'captcha_image_url': image_url
    })