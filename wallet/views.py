from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Wallet, Transaction
from orders.models import OrderItem
from django.http import JsonResponse
from decimal import Decimal
# Create your views here.



#######################  wallet-page  ###################

def wallet_page(request):
    
    return render(request,'wallet/wallet-page.html')


##########################  orderitem cacelling logic   ####################

def cancell_order_item(request, order_item_id):
    # Ensure it's a POST request for safety
    if request.method == 'POST':
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