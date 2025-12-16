from django.shortcuts import render,get_object_or_404,redirect
from .models import Wishlist
from products.models import ProductVariant
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from cart.models import Cart

#####################  wish list page    ##################

@login_required(login_url='user_side:sign-in')
def wishlist_page(request):
    if request.user.is_authenticated:
        wishlist_items=Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items=[]
        
    cart_product_ids = []

    try:
        cart = Cart.objects.get(user=request.user)
        cart_product_ids = list(
            cart.items.values_list('product_variant_id', flat=True)
        )
    except Cart.DoesNotExist:
        pass

    context={
        'wishlist_items':wishlist_items,
        'cart_product_ids': cart_product_ids,
    }
    return render(request,'wishlist/wishlist-page.html',context)

#####################  add product to the wish list   ####################

def add_to_wishlist(request):
    product_variant_id = request.GET.get('id')
    context = {}

    if not request.user.is_authenticated:
        context['bool'] = False
        context['message'] = "Login required to add products to wishlist."
        return JsonResponse(context)

    try:
        product_variant = ProductVariant.objects.get(id=product_variant_id)
    except ProductVariant.DoesNotExist:
        messages.error(request, "Product variant not found.")
        context['bool'] = False
        return JsonResponse(context)

    # Check if the product variant is already in the user's wishlist
    wishlist_exists = Wishlist.objects.filter(product_variant=product_variant, user=request.user).exists()

    if wishlist_exists:
        context['bool'] = True
        context['message'] = "Product is already in your wishlist."
    else:
        Wishlist.objects.create(
            product_variant=product_variant,
            user=request.user,
        )
      
        context['bool'] = True
        context['message'] = "Added to wishlist successfully."

    return JsonResponse(context)

########################  delete product from wishlist  ########################

@login_required(login_url='user_side:sign-in')
def delete_wishlist(request,wishlist_id):
    wishlist=get_object_or_404(Wishlist,id=wishlist_id)
    wishlist.delete()
    messages.success(request, 'Item successfully removed from your wishlist.')
    return redirect('wishlist:wishlist-page')

###################  Show wish list count dynamiccally using fetch api  #######################

@login_required(login_url='user_side:sign-in')
def wishlist_count(request):
    # Get the count of wishlist items for the logged-in user
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({'count': count})

