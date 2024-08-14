from django.shortcuts import render
from products.models import ProductVariant

# Create your views here.

#######################  user home-side #####################################3

def Index(request):
    product_variants=ProductVariant.objects.all()
    context={
        'product_variants':product_variants,
    }
    return render(request,'core/index.html',context)

##################  To show/list products in the user side ####################################

