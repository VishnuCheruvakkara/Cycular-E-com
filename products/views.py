from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm,ProductVariantForm,CategoryForm,BrandForm,SizeForm
from django.contrib import messages
from .models import Product,ProductVariant
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.views.decorators.http import require_POST
from .models import Category,Brand,Size
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



# Create your views here.

###################### Product Management page #################################

def ProductManagement(request):
    products=Product.objects.all()

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

###################### Add product page #################################

def AddProduct(request):
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


###################### Edit productpage Management page #################################

def EditProduct(request,product_id):
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

####################### delete product ########################################

def DeleteProduct(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    product.delete()
    messages.success(request, 'Selected Product was successfully deleted.',extra_tags='admin}')
    return redirect('products:product-management')

####################### image resize function  ########################################


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

####################### add product varient  ########################################

def product_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductVariantForm(request.POST, request.FILES, product=product)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product 

          

            # Process and resize the cropped images
            for i in range(1, 4):
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

##################  Product soft-delete  ####################################

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

##################  Product View  ####################################

def product_view(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    product_variants=product.product_variants.all()
                                                                   
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

################## product category  page ################################


def category_management(request):
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
   
    
    context = {
        'categories': categories,
        'brands': brands,
        'sizes':sizes,
        'form': form  # Include the form in the context
    }
    
    return render(request, 'products/product-category-management.html', context)

##################### Delete Category ############################

def delete_category(request,category_id):
    category=get_object_or_404(Category,id=category_id)
    category.delete()
    messages.success(request,'Category deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

##################### Delete Brand  ##############################

def delete_brand(request,brand_id):
    brand=get_object_or_404(Brand,id=brand_id)
    brand.delete()
    messages.success(request,'Brand deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

#################### Delete Size ########################

def delete_size(request,size_id):
    size=get_object_or_404(Size,id=size_id)
    size.delete()
    messages.success(request,'Size deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

################## add category ################################

def add_category(request):
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

################## edit category ################################

def edit_category(request,category_id):
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


############################ add-brand ##################################

def add_brand(request):
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

############################ edit-brand #################################

def edit_brand(request,brand_id):
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

############################ add-size ##################################

def add_size(request):
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

############################ edit-size #################################

def edit_size(request,size_id):
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

####################### delete product variant ########################################

def delete_product_variant(request,variant_id):
    variant=get_object_or_404(ProductVariant,id=variant_id)
    product_id=variant.product.id
    variant.delete()
    messages.success(request, 'Selected Product Variant was successfully deleted.',extra_tags='admin}')
    return redirect('products:product-view',product_id=product_id)


####################### edit variant  ################################


def edit_variant(request, variant_id):
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

######################## single product view  #########################

def single_product_view(request, variant_id):
    variant=get_object_or_404(ProductVariant,id=variant_id)
    sizes=Size.objects.all()
    context={
        'variant':variant,
        'sizes':sizes,
    }
    return render(request, 'products/single-product.html',context)

########################### product-variant-data-view #######################

def product_variant_data(request,variant_id):
    variant=get_object_or_404(ProductVariant,id=variant_id)
    context={
        'variant':variant,
        'product':variant.product
    }
    return render(request,'products/product-variant-data-view.html',context)

#####################  product stock count  by size using ajax  #########################


def get_size_stock(request):
    size_id = request.GET.get('size_id')
    product_id = request.GET.get('product_id')  # Assuming you need product_id to find the relevant ProductVariant

    if size_id and product_id:
        try:
            # Retrieve the ProductVariant based on size_id and product_id
            variant = ProductVariant.objects.get(size_id=size_id, product_id=product_id)
            stock = variant.stock
            return JsonResponse({'stock': stock})
        except ProductVariant.DoesNotExist:
            return JsonResponse({'stock': 0})
    return JsonResponse({'stock': 0})