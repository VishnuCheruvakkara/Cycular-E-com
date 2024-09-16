from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Wallet, Transaction
from orders.models import OrderItem
from django.http import JsonResponse
from decimal import Decimal
import json
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
# Create your views here.



#######################  wallet-page  ###################

def wallet_page(request):
    
    return render(request,'wallet/wallet-page.html')


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
            captcha_store = CaptchaStore.objects.get(hashkey=captcha_key)  # Query by hashkey
            if captcha_store.response != captcha_response:
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
        order_item.save()

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