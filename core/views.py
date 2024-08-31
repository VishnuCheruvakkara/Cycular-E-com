from django.shortcuts import render
from products.models import ProductVariant
from django.views.decorators.cache import never_cache

# Create your views here.

#######################  user home-side #####################################

@never_cache
def Index(request):
    product_variants=ProductVariant.objects.filter(status=True,product__status=True)
    context={
        'product_variants':product_variants,
    }
    return render(request,'core/index.html',context)

##################  To show the category based seletection and filtering  ####################################

def category_filter(request):
    
    return render(request,'core/category-filter.html')