from django.shortcuts import render,get_object_or_404,redirect
from .models import Wishlist
from products.models import Product,ProductVariant
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
#####################  wish list page    ##################
def wishlist_page(request):
    if request.user.is_authenticated:
        wishlist_items=Wishlist.objects.filter(user=request.user)
    else:
        wishlist_items=[]
    context={
        'wishlist_items':wishlist_items,
    }
    return render(request,'wishlist/wishlist-page.html',context)


#####################  add product to the wish list   ####################


def add_to_wishlist(request):
    product_variant_id=request.GET['id']
    product_variant=ProductVariant.objects.get(id=product_variant_id)

    context={

    }
    wishlist_count=Wishlist.objects.filter(product_variant=product_variant,user=request.user).count()
    print(wishlist_count)
    if wishlist_count > 0:
        context={
            "bool":True
        }
    else:
        new_wishlist=Wishlist.objects.create(
            product_variant=product_variant,
            user=request.user,
        )
        context={
            "bool":True
        }
    return JsonResponse(context)

########################  delete product from wishlist  ########################

def delete_wishlist(request,wishlist_id):
    wishlist=get_object_or_404(Wishlist,id=wishlist_id)
    wishlist.delete()
    messages.success(request, 'Item successfully removed from your wishlist.')
    return redirect('wishlist:wishlist-page')
 