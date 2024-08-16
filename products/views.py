from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm,ProductVariantForm,Size
from django.contrib import messages
from .models import Product,ProductVariant
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image



# Create your views here.

###################### Category Management page #################################

def CategoryManagement(request):
    products=Product.objects.all()
    return render(request,'products/category-management.html',{'products':products})

###################### Add product page #################################

def AddProduct(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been successfully added.')
            return redirect('products:category-management')  # Redirect to a success URL or product list
        else:
            messages.error(request, 'There were errors in the form. Please correct them and try again.')
    else:
        form = ProductForm()
    return render(request, 'products/add-product.html', {'form': form})


###################### Edit productpage Management page #################################

def EditProduct(request,product_id):
    product=get_object_or_404(Product,id=product_id)
    if request.method =='POST':
        form = ProductForm(request.POST,request.FILES,instance=product)
        if form.is_valid:
            form.save()
            return redirect('products:category-management')
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
    return redirect('products:category-management')

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

def ProductVariantViews(request, product_id):
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
            return redirect('products:category-management')
        else:
            messages.error(request, 'There was an error with your form submission. Please check the details and try again.',extra_tags='admin')
    else:
        form = ProductVariantForm(product=product)

    context = {
        'form': form,
        'product': product,
    }

    return render(request, 'products/variant-product.html', context)

#################### single priduct page  ###############################

def SingleProduct(request,variant_id):
    product_variant = get_object_or_404(ProductVariant, id=variant_id)
    product = product_variant.product
    product_variants = ProductVariant.objects.filter(product=product)
    related_products=Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    sizes=Size.objects.all()

    
    context = {
        'product': product,  # The main product
        'product_variant': product_variant,  # The specific variant passed in the URL
        'product_variants': product_variants,  # All variants of the product for filtering
        'sizes':sizes,
    }
    return render(request,'products/product-detail.html',context)
##################  Product soft-delete  ####################################
  
def toggle_product_status(request, product_id):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        product.status = not product.status
        product.save()
        return JsonResponse({'status': product.status, 'message': 'Status updated successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)


######################### Get stock from the database #####################

def get_stock(request):
    size_id = request.GET.get('size_id')
    try:
        product_size = Size.objects.get(id=size_id)
        stock = product_size.stock
    except Size.DoesNotExist:
        stock = 0

    return JsonResponse({'stock': stock})
