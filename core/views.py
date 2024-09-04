from django.shortcuts import render
from products.models import ProductVariant
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models.functions import Lower
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
    sort_by = request.GET.get('sortby','default')
    product_variants = ProductVariant.objects.filter(status=True)
    # Apply sorting
    if sort_by == 'increase':
        product_variants = product_variants.order_by('price')  # Low to high
    elif sort_by == 'decrease':
        product_variants = product_variants.order_by('-price')  # High to low
    elif sort_by == 'new':
        product_variants = product_variants.order_by('-created_at')  # New arrivals (assuming you have a 'created_at' field)
    elif sort_by == 'alpha-increase':
        product_variants = product_variants.order_by(Lower('product__name'))  # A-Z
    elif sort_by == 'alpha-decrease':
        product_variants = product_variants.order_by(Lower('product__name').desc())  # Z-A


    
    paginator = Paginator(product_variants, 5)  
    page = request.GET.get('page')

    try:
        paginated_variants = paginator.page(page)
    except PageNotAnInteger:
        paginated_variants = paginator.page(1)
    except EmptyPage:
        paginated_variants = paginator.page(paginator.num_pages)

    product_variant_counts = product_variants.count()
    context = {
        'product_variants': paginated_variants,  # Pass paginated variants to the template
        'product_variant_counts': product_variant_counts,  # Total count of product variants
        'sort_by': sort_by,
    }
    return render(request, 'core/category-filter.html', context)


