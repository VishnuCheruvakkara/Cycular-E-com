from django.shortcuts import render,get_object_or_404
from cart.models import Cart,CartItem

# Create your views here.

def check_out(request):
    #retrive the current user's cart
    cart=get_object_or_404(Cart,user=request.user)
    #retrive all items for the current user cart
    cart_items=cart.items.all() #items is the related name
    
    #total price of product
    total_price=sum(item.subtotal for item in cart_items)
  
    context={
        'cart_items':cart_items,
        'total_price':total_price,
    }
    return render(request,'payment/check-out.html',context)
