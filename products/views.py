from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm,ProductVariantForm,CategoryForm,BrandForm,SizeForm,ColorForm
from django.contrib import messages
from .models import Product,ProductVariant
from orders.models import OrderItem
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.views.decorators.http import require_POST
from .models import Category,Brand,Size,Color,ProductReview
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from wishlist.models import Wishlist
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.db import IntegrityError

###################### Product Management page Admin side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def ProductManagement(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    # Get the search query
    query = request.GET.get('q', '')

    products=Product.objects.all()
        
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    # Set up pagination.
    paginator = Paginator(products, 5)  
    page = request.GET.get('page')
    try:
        products_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_paginated = paginator.page(1)
    except EmptyPage:
        products_paginated = paginator.page(paginator.num_pages)
    context={
        'products':products_paginated,
    }
    return render(request,'products/product-management.html',context)

###################### Add product page Admin side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def AddProduct(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been successfully added.',extra_tags='admin')
            return redirect('products:product-management')  # Redirect to a success URL or product list
        else:
            messages.error(request, 'There were errors in the form. Please correct them and try again.',extra_tags='admin')
    else:
        form = ProductForm()
    return render(request, 'products/add-product.html', {'form': form})

###################### Edit productpage Management page Admin side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def EditProduct(request,product_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    product=get_object_or_404(Product,id=product_id)
    if request.method =='POST':
        form = ProductForm(request.POST,request.FILES,instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!',extra_tags='admin')
            return redirect('products:product-management')
        else:
            messages.error(request, 'There was an error updating the product. Please check the form for errors.',extra_tags='admin')
    else:
        form=ProductForm(instance=product)
    context={
        'form':form,
        'product':product,
    }
    return render(request,'products/edit-product.html',context)

####################### delete product Admin side ########################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def DeleteProduct(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    product.delete()
    messages.success(request, 'Selected Product was successfully deleted.',extra_tags='admin}')
    return redirect('products:product-management')

####################### image resize function Admin side ########################################

def ResizeImage(image, max_width=800, max_height=600,filename=None):
    # Open the image file
    img = Image.open(image)
    
    # Calculate the appropriate size while maintaining the aspect ratio
    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Save the image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, format=img.format, quality=85)
    
    # Create a ContentFile from the BytesIO object
    img_file = ContentFile(img_io.getvalue(), name=filename if filename else 'resized_image.jpg')
    
    return img_file

####################### add product varient Admin side ########################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def product_variant(request, product_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, product=product)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product 

            # Process and resize the cropped images
            for i in range(1, 5):
                cropped_data = request.POST.get(f'image{i}_cropped_data')
                if cropped_data:
                    try:
                        format, imgstr = cropped_data.split(';base64,')
                        ext = format.split('/')[-1]
                        img_data = base64.b64decode(imgstr)
                        
                        # Use BytesIO to create a file-like object
                        img_io = BytesIO(img_data)
                        
                        # Resize the image
                        resized_img = ResizeImage(img_io, max_width=800, max_height=600)
                        
                        # Assign the resized image to the variant
                        setattr(variant, f'image{i}', resized_img)
                    except (ValueError, IndexError, base64.binascii.Error) as e:
                        # Handle exceptions or errors in image data processing
                        messages.error(request, f"Error processing image {i}: {str(e)}",extra_tags='admin')
                        pass

            variant.save()
            messages.success(request, 'Product variant has been successfully created.',extra_tags='admin')
            return redirect('products:product-view',product_id=product_id)
        else:
            messages.error(request, 'There was an error with your form submission. Please check the details and try again.',extra_tags='admin')
    else:
        form = ProductVariantForm(product=product)

    context = {
        'form': form,
        'product': product,
        'non_field_errors': form.non_field_errors() 
    }

    return render(request, 'products/variant-product.html', context)

##################  Product soft-delete  Admin side ####################################

@login_required(login_url='admin_side:seller-login')
@never_cache
@require_POST
def toggle_product_status(request):
    product_id = request.POST.get('product_id')
    try:
        product = Product.objects.get(id=product_id)
        product.status = not product.status
        product.save()
        return JsonResponse({'success': True, 'status': product.status})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})

##################  Product View Admin side ####################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def product_view(request,product_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    product=get_object_or_404(Product,id=product_id)
    product_variants=product.product_variants.all()
        
    # Check for the search parameter
    search_query = request.GET.get('query', '').strip()

    # Initialize the filter conditions
    filter_conditions = Q()

    # Only proceed if the search query is not empty
    if search_query:
        # Split the search query by comma or space
        search_terms = [term.strip() for term in search_query.split(',')]

        for term in search_terms:
            # Add conditions for color and size
            filter_conditions |= Q(color__name__iexact=term) | Q(size__name__iexact=term)

        # Apply the filter
        product_variants = product_variants.filter(filter_conditions).distinct()
    
    # Set up pagination.
    paginator = Paginator(product_variants, 5)  
    page = request.GET.get('page')
    try:
        products_variants_paginated = paginator.page(page)
    except PageNotAnInteger:
        products_variants_paginated = paginator.page(1)
    except EmptyPage:
        products_variants_paginated = paginator.page(paginator.num_pages)
    context={      
        'product':product,
        'product_variants':products_variants_paginated,
    }
    return render(request,'products/product-view.html',context)

################## product category  page  Admin side ################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def category_management(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:category-add')  # Redirect to the same page to display the new category
    else:
        form = CategoryForm()
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    sizes = Size.objects.all()
    colors= Color.objects.all()
   
    context = {
        'categories': categories,
        'brands': brands,
        'sizes':sizes,
        'colors':colors,
        'form': form,# Include the form in the context
    }
    
    return render(request, 'products/product-category-management.html', context)

##################### Delete Category Admin side ############################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_category(request,category_id):
    category=get_object_or_404(Category,id=category_id)
    category.delete()
    messages.success(request,'Category deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')   

##################### Delete Brand Admin side ##############################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_brand(request,brand_id):
    brand=get_object_or_404(Brand,id=brand_id)
    brand.delete()
    messages.success(request,'Brand deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

#################### Delete Size Admin side ########################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_size(request,size_id):
    size=get_object_or_404(Size,id=size_id)
    size.delete()
    messages.success(request,'Size deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

################### Delete Color Admin side ##########################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_color(request,color_id):
    color=get_object_or_404(Color,id=color_id)
    color.delete()
    messages.success(request,'Color deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

################## add category Admin Side ################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def add_category(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    heading="Add-Category"
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Product added successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error,try again!',extra_tags='admin')
           
    else:
        form = CategoryForm()
    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-category.html',context)

################## edit category Admin Side Admin Side ################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_category(request,category_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    category=get_object_or_404(Category,id=category_id)
    heading="Edit-Category"
    if request.method == 'POST':
        form = CategoryForm(request.POST,instance=category)
      
        if form.is_valid():
            form.save()
            messages.success(request,'Category updated successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error, try again!',extra_tags='admin')
    else:
        form=CategoryForm(instance=category)

    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-category.html',context)

############################ add-brand Admin Side ##################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def add_brand(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    heading="Add-Brand"
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Brand added successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error,try again!',extra_tags='admin')
    else:
        form = BrandForm()
    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-brand.html',context)

############################ edit-brand Admin Side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_brand(request,brand_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    brand=get_object_or_404(Brand,id=brand_id)
    heading="Edit-Brand"
    if request.method == 'POST':
        form = BrandForm(request.POST,instance=brand)

        if form.is_valid():
            form.save()
            messages.success(request,'Brand updated successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error, try again!',extra_tags='admin')
    else:
        form=BrandForm(instance=brand)

    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-brand.html',context)

############################ add-size Admin Side ##################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def add_size(request):
    if not request.user.is_superuser:
        return redirect('core:index')
    heading="Add-Size"
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Size added successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error,try again!',extra_tags='admin')
           
    else:
        form = SizeForm()
    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-size.html',context)

############################ edit-size Admin Side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_size(request,size_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    size=get_object_or_404(Size,id=size_id)
    heading="Edit-Size"
    if request.method == 'POST':
        form = SizeForm(request.POST,instance=size)
        if form.is_valid():
            form.save()
            messages.success(request,'Size updated successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error, try again!',extra_tags='admin')
    else:
        form=SizeForm(instance=size)

    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-size.html',context)

############################ add-color Admin Side ##################################d

@login_required(login_url='admin_side:seller-login')
@never_cache
def add_color(request):
    if request.method == 'POST':
        form = ColorForm(request.POST)
        if form.is_valid():
            # Save the color to the database
            form.save()
            return redirect('products:category-add')  # Redirect to a relevant page
    else:
        form = ColorForm()  # Create an empty form for GET requests

    # Render the add color template with the form
    context = {
        'form': form,
        'heading': 'Add New Color',  # Set a heading for the page
    }
    return render(request, 'products/add-color.html', context)

############################ edit-color Admin Side #################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_color(request,color_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    color=get_object_or_404(Color,id=color_id)
    heading="Edit-Color"
    if request.method == 'POST':
        form = ColorForm(request.POST,instance=color)
        if form.is_valid():
            form.save()
            messages.success(request,'Color updated successfully!',extra_tags='admin')
            return redirect('products:category-add')
        else:
            messages.error(request,'Please correct the error, try again!',extra_tags='admin')
    else:
        form=ColorForm(instance=color)

    context={
        'form':form,
        'heading':heading,
    }
    return render(request,'products/add-color.html',context)

####################### delete product variant Admin side ########################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_product_variant(request,variant_id):
    variant=get_object_or_404(ProductVariant,id=variant_id)
    product_id=variant.product.id
    variant.delete()
    messages.success(request, 'Selected Product Variant was successfully deleted.',extra_tags='admin}')
    return redirect('products:product-view',product_id=product_id)

####################### edit variant Admin side ################################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_variant(request, variant_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    product_id = product.id
    
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, instance=variant)
        
        if form.is_valid():
            # Handling the cropped images
            image1_cropped_data = request.POST.get('image1_cropped_data')
            image2_cropped_data = request.POST.get('image2_cropped_data')
            image3_cropped_data = request.POST.get('image3_cropped_data')
            image4_cropped_data = request.POST.get('image4_cropped_data')  # Handling the 4th image

            if image1_cropped_data:
                format, imgstr = image1_cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                image1_file = ContentFile(base64.b64decode(imgstr), name=f'{variant.product}_image1.{ext}')
                variant.image1 = image1_file

            if image2_cropped_data:
                format, imgstr = image2_cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                image2_file = ContentFile(base64.b64decode(imgstr), name=f'{variant.product}_image2.{ext}')
                variant.image2 = image2_file

            if image3_cropped_data:
                format, imgstr = image3_cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                image3_file = ContentFile(base64.b64decode(imgstr), name=f'{variant.product}_image3.{ext}')
                variant.image3 = image3_file

            if image4_cropped_data:  # New code for handling the 4th image
                format, imgstr = image4_cropped_data.split(';base64,')
                ext = format.split('/')[-1]
                image4_file = ContentFile(base64.b64decode(imgstr), name=f'{variant.product}_image4.{ext}')
                variant.image4 = image4_file  # Assuming your model has `image4` field

            variant.save()
            messages.success(request, 'Product Variant was edited successfully.', extra_tags='admin')
            return redirect('products:product-view', product_id=product_id)
        else:
            messages.error(request, 'Please correct the following error!', extra_tags='admin')
    else:
        form = ProductVariantForm(instance=variant, product=product)

    context = {
        'form': form,
        'product_id': product_id,
        'product': product
    }
    return render(request, 'products/edit-variant.html', context)

######################## single product view User side  #########################

def single_product_view(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    available_variants = ProductVariant.objects.filter(product=variant.product).values('id', 'size__name', 'color__name').distinct()
    product = variant.product
    related_variants = ProductVariant.objects.filter(product__category=product.category).exclude(id=variant.id)[:5]

       # Fetch the discounted price and maximum discount percentage
    discounted_price = variant.get_discounted_price()
    max_discount_percentage = variant.get_discount_percentage()
    
    # Check if the product variant exists in the user's cart
    cart_item_exists = (
        request.user.is_authenticated and 
        CartItem.objects.filter(cart__user=request.user, product_variant=variant).exists()
    )

    wishlist_item_exists = (
        request.user.is_authenticated and 
        Wishlist.objects.filter(user=request.user, product_variant=variant).exists()
    )

    reviews = variant.product.reviews.all().order_by('-created_at')

    
    has_reviewed = False
    has_purchased = False
    can_review = False

    if request.user.is_authenticated:
        has_reviewed = variant.product.reviews.filter(
            user=request.user
        ).exists()

        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            order_item_status='Delivered',
            product_variant__product=variant.product
        ).exists()

        can_review = has_purchased and not has_reviewed

    review_stats = product.get_review_stats()

    # Review stats for related variants
    related_variants_stats = {}
    for rv in related_variants:
        stats = rv.product.get_review_stats()
        related_variants_stats[rv.id] = stats


   
    context = {
        'variant': variant,
        'available_variants': available_variants,
        'related_variants': related_variants,
        'related_variants_stats': related_variants_stats,
        'cart_item_exists': cart_item_exists,
        'wishlist_item_exists': wishlist_item_exists,
        'max_discount_percentage': max_discount_percentage,  # Pass the maximum discount percentage
        'discounted_price': discounted_price,  # Add discounted price
        'original_price': variant.price,  # Add original price
        'reviews': reviews, 
        'has_reviewed': has_reviewed,
        'has_purchased': has_purchased,
        'can_review': can_review,
        'review_stats': review_stats,
    }
    
    return render(request, 'products/single-product.html', context)


########################### product-variant-data-view admin-side #######################

@login_required(login_url='admin_side:seller-login')
@never_cache
def product_variant_data(request,variant_id):
    if not request.user.is_superuser:
        return redirect('core:index')
    variant=get_object_or_404(ProductVariant,id=variant_id)
    context={
        'variant':variant,
        'product':variant.product,
    }
    return render(request,'products/product-variant-data-view.html',context)


###########################  Review system userside #########################

@login_required(login_url='user_side:sign-in')
def add_product_review(request):
    try:
        product_variant_id = request.POST.get("variant_id")
        rating = int(request.POST.get("rating"))
        title = request.POST.get("title").strip()
        review_text = request.POST.get("review").strip()

        if not all([product_variant_id, rating, title, review_text]):
            return JsonResponse({
                "status": "error",
                "message": "All fields are required."
            }, status=400)

        if rating < 1 or rating > 5:
            return JsonResponse({
                "status": "error",
                "message": "Rating must be between 1 and 5."
            }, status=400)

        variant = get_object_or_404(ProductVariant, id=product_variant_id)

        ProductReview.objects.create(
            product=variant.product,
            user=request.user,
            rating=rating,
            title=title,
            review=review_text
        )

        return JsonResponse({
            "status": "success",
            "message": "Review submitted successfully."
        })

    except IntegrityError:
        return JsonResponse({
            "status": "error",
            "message": "You have already reviewed this product."
        }, status=409)

    except Exception:
        return JsonResponse({
            "status": "error",
            "message": "Something went wrong. Please try again."
        }, status=500)


