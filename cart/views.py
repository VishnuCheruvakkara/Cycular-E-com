from django.shortcuts import render,get_object_or_404
from products.models import ProductVariant
from .models import Cart,CartItem
from django.contrib import messages

# Create your views here.

def cart(request):
    
    return render(request,'cart/cart.html')

#################  add product to the cart  ################

def add_to_cart(request):
    if request.method == 'POST':
            # get the product variant id 
            product_variant_id=request.POST.get('product_variant_id')
            product_variant=get_object_or_404(ProductVariant,id=product_variant_id)

            #get or creat cart for the current user
            cart,created=Cart.objects.get_or_create(user=request.user)

            #check that the product varint is already is in the cart 
            cart_item,item_created=CartItem.objects.get_or_create(cart=cart,product_variant=product_variant)

            if not item_created:
                cart_item.quantity += 1
            else:
                cart_item.quantity = 1

            #Save the cart item
            cart_item.save()

            #success message
            messages.success(request, 'Product added to cart successfully!')
            

            