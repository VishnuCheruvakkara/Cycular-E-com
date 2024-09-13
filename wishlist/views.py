from django.shortcuts import render,get_object_or_404
from .models import Wishlist
from products.models import Product,ProductVariant
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
#####################  wish list page    ##################
def wishlist_page(request):
    
    return render(request,'wishlist/wishlist-page.html')


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