from django.shortcuts import render,get_object_or_404,redirect
from products.models import ProductVariant
from .models import Cart,CartItem
from django.contrib import messages
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required

##################   main cart page...   ########################

@login_required(login_url='user_side:sign-in') 
def cart(request):
    if not request.user.is_authenticated:
        return redirect('core:index')
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_items=cart.items.all()

    out_of_stock_items = [
        item.product_variant.product.name
        for item in cart_items
        if item.quantity > item.product_variant.stock
    ]

    overall_total = sum(item.subtotal for item in cart_items)
    total_quantity=sum(item.quantity for item in cart_items)
 
    context={
        'carts':cart,
        'cart_items':cart_items,
        'overall_total': overall_total,
        'total_quantity':total_quantity,
        'out_of_stock_items': out_of_stock_items,

    }
    return render(request,'cart/cart.html',context)

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

    # Check if the stock is zero
    if action == 'add':
          # Check if the product variant has stock available
        if product_variant.stock <= 0:
            # Return an error message if the product is out of stock
            return JsonResponse({'status': 'error', 'message': 'This product is currently out of stock. Please check back later.'})
    
        # Add the product to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_variant=product_variant)
        if created:
            # If the item was just created, set the quantity to 1
            cart_item.quantity = 1
            cart_item.save()
            return JsonResponse({'status': 'success', 'message': 'Product added to your cart.'})
        else:
            # If the item already exists, show an error message or update as needed
            return JsonResponse({'status': 'info', 'message': 'This product is already in your cart, Check your cart.'})

    elif action == 'remove':
        # Remove the product from the cart
        cart_item = CartItem.objects.filter(cart=cart, product_variant=product_variant).first()
        if cart_item:
            cart_item.delete()
            return JsonResponse({'status': 'success', 'message': 'Product removed from your cart.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid action.'})

##############################  update the count of item in the add to cart button in home page  ########################

@login_required(login_url='user_side:sign-in')
def get_cart_count(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

    user = request.user
    cart = Cart.objects.filter(user=user).first()
    count = 0
    if cart:
        count = cart.items.count()

    return JsonResponse({'status': 'success', 'count': count})

##########################  remove product from  cart with page reload  ##########################

@login_required(login_url='user_side:sign-in')
def remove_from_cart(request,cart_item_id):
    cart_item=get_object_or_404(CartItem,id=cart_item_id)
    cart_item.delete()
    messages.success(request, 'Item successfully removed from your cart.')
    return redirect('cart:cart-page')

######################## update cart quantity of a product based on the count and stock  ###################

@login_required(login_url='user_side:sign-in')
def update_cart_item_quantity(request, cart_item_id):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 0))
        max_quantity_limit = 5 

        if quantity > max_quantity_limit:
            return JsonResponse({
                'status': 'error',
                'message': f'Maximum limit exceeded. You can only add up to {max_quantity_limit} of this product.'
            })
        
        if 1 <= quantity <= cart_item.product_variant.stock:
            cart_item.quantity = quantity
            cart_item.save()

            # Use discounted price if available, otherwise fallback to regular price
            discounted_price = cart_item.product_variant.get_discounted_price()
            price_to_use = discounted_price if discounted_price < cart_item.product_variant.price else cart_item.product_variant.price
            new_total = cart_item.quantity * float(price_to_use)

            # Calculate the overall cart total price, taking discounts into account
            cart_items = CartItem.objects.filter(cart=cart_item.cart)
            overall_total = sum(
                item.quantity * float(
                    item.product_variant.get_discounted_price() if item.product_variant.get_discounted_price() < item.product_variant.price else item.product_variant.price
                ) for item in cart_items
            )
            
            return JsonResponse({'status': 'success', 'new_total': new_total, 'overall_total': overall_total})
        else:
            available_stock = cart_item.product_variant.stock
            return JsonResponse({'status': 'error', 'message': f'Quantity is out of stock. Only {available_stock} quantity in stock.'})
    
    except (ValueError, KeyError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data provided.'})
