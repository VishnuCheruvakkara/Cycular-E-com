from django.shortcuts import render
from products.models import ProductVariant
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models.functions import Lower
from products.models import Category,Brand,Size,Color
from django.db.models import Min,Max,Count,Q
from wishlist.models import Wishlist
from urllib.parse import urlencode

#######################  user home-side #####################################

@never_cache
def Index(request):
    product_variants=ProductVariant.objects.filter(status=True,product__status=True)
    
    if request.user.is_authenticated:
        user_wishlist_ids=set(Wishlist.objects.filter(user=request.user).values_list('product_variant_id',flat=True))
    else:
        user_wishlist_ids=set()

    context={
        'product_variants':product_variants,
        'user_wishlsit_ids':user_wishlist_ids,
    }
    return render(request,'core/index.html',context)

##################  To show the category based seletection and filtering  ####################################

def category_filter(request):

    if request.user.is_authenticated:
        user_wishlist_ids=set(Wishlist.objects.filter(user=request.user).values_list('product_variant_id',flat=True))
    else:
        user_wishlist_ids=set()

    sort_by = request.GET.get('sortby','default')

   # Get and filter out empty values
    selected_categories = list(filter(None, request.GET.getlist('categories')))
    selected_sizes = list(filter(None, request.GET.getlist('sizes')))
    selected_brands = list(filter(None, request.GET.getlist('brands')))
    selected_colors = list(filter(None, request.GET.getlist('colors')))
    # Get price range from GET parameters
    Min_price = request.GET.get('min_price', None)
    Max_price = request.GET.get('max_price', None)

    # Get the search term from the GET parameters
    search_query = request.GET.get('search', '').strip()

    product_variants = ProductVariant.objects.filter(status=True)

    # Fetch the price range from the database
    price_range = product_variants.aggregate(min_price=Min('price'), max_price=Max('price'))
    
    # Apply search filter if a search term is entered
    if search_query:
        product_variants = product_variants.filter(
            Q(product__name__icontains=search_query) | 
            Q(product__description__icontains=search_query)
        )
  
    # Apply category filter if any categories are selected
    if selected_categories:
        product_variants=product_variants.filter(product__category_id__in=selected_categories)

    if selected_sizes:
        product_variants = product_variants.filter(size__id__in=selected_sizes)

    if selected_colors:  # Apply color filter
        product_variants = product_variants.filter(color__id__in=selected_colors)
    if selected_brands:
        product_variants=product_variants.filter(product__brand__id__in=selected_brands)

    # Apply price range filter if min_price and max_price are provided
    if Min_price and Max_price:
        product_variants = product_variants.filter(price__gte=Min_price, price__lte=Max_price)

    #Fetch all the active categories...
    categories = Category.objects.annotate(
        product_variant_count=Count('products__product_variants', filter=Q(products__product_variants__status=True))
    )
    
    brands = Brand.objects.filter(status=True)
    sizes = Size.objects.filter(status=True)
    colors = Color.objects.filter(status=True) 

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

    paginator = Paginator(product_variants, 8)  
    page = request.GET.get('page')

    try:
        paginated_variants = paginator.page(page)
    except PageNotAnInteger:
        paginated_variants = paginator.page(1)
    except EmptyPage:
        paginated_variants = paginator.page(paginator.num_pages)

    product_variant_counts = product_variants.count()
    
    querydict = request.GET.copy()
    querydict.pop('page', None)
    query_string = querydict.urlencode()

    context = {
        'product_variants': paginated_variants,  # Pass paginated variants to the template
        'product_variant_counts': product_variant_counts,  # Total count of product variants
        'sort_by': sort_by,
        'categories': categories,
        'brands': brands,
        'sizes': sizes,
        'colors': colors,
        'price_range': price_range,
        'selected_categories': selected_categories,
        'selected_sizes': selected_sizes,
        'selected_colors': selected_colors,
        'selected_brands':selected_brands,
        'selected_min_price': Min_price,
        'selected_max_price': Max_price,
        'search_query': search_query,
        'user_wishlist_ids': user_wishlist_ids,
        'query_string': query_string,
    }
    return render(request, 'core/category-filter.html', context)




