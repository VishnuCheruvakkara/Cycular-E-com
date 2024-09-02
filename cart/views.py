from django.shortcuts import render,get_object_or_404,redirect
from products.models import ProductVariant
from .models import Cart,CartItem
from django.contrib import messages
from django.http import JsonResponse
# Create your views here.

def cart(request):
    
    return render(request,'cart/cart.html')

#################  add product to the cart  ################

def add_to_cart(request):
    if not request.user.is_authenticated:
       return JsonResponse({'status': 'error', 'message': 'Please login to add products to your cart.'}, status=401)
    
    #get or crate user cart 
    user=request.user
    cart,created=Cart.objects.get_or_create(user=user)

    #get the product varian id from the cart 
    product_variant_id=request.POST.get('product_variant_id')
    action = request.POST.get('action')
    product_variant=get_object_or_404(ProductVariant,id=product_variant_id)

    if action == 'add':
        # Add product to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_variant=product_variant)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return JsonResponse({'status': 'success', 'message': 'Product added to your cart.'})
    elif action == 'remove':
        # Remove product from the cart
        cart_item = CartItem.objects.filter(cart=cart, product_variant=product_variant).first()
        if cart_item:
            cart_item.delete()
            return JsonResponse({'status': 'success', 'message': 'Product removed from your cart.'})
    

    return JsonResponse({'status':'success','message':'Product added to your cart.'})
