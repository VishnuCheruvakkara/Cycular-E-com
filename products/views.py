from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm,ProductVariantForm,CategoryForm
from django.contrib import messages
from .models import Product
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.views.decorators.http import require_POST
from .models import Category,Brand,Size,Color



# Create your views here.

###################### Category Management page #################################

def ProductManagement(request):
    products=Product.objects.all()
    return render(request,'products/product-management.html',{'products':products})

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

def ProductVariant(request, product_id):
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
    context={
        'product':product,
        'product_variants':product_variants,
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
    colors = Color.objects.all()
    
    context = {
        'categories': categories,
        'brands': brands,
        'sizes': sizes,
        'colors': colors,
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

#################### Delete Color ########################

def delete_color(request,color_id):
    color=get_object_or_404(Color,id=color_id)
    color.delete()
    messages.success(request,'Color deleted successfully.',extra_tags='admin')
    return redirect('products:category-add')

################## add category ################################

def add_category(request):

    return render(request,'products/add-category.html')