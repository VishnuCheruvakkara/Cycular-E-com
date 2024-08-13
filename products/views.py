from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm,ProductVariantForm
from django.contrib import messages
from django.conf import settings
from .models import Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

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

####################### add product varient  ########################################

def ProductVariant(request,product_id):
    product=get_object_or_404(Product,id=product_id)

    if request.method=='POST':
        form=ProductVariantForm(request.POST,request.FILES,product=product)
        if form.is_valid():
            variant=form.save(commit=False)
            variant.product=product
            variant.save()
            return redirect('products:category-management')
    else:
        form=ProductVariantForm(product=product)
    context={
        'variant':form,
        'product':product,
        
    }
    return render(request,'products/variant-product.html',context)


##################  Add product-variant-image to the database ####################################

def UploadImages(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')

        image_paths = {}
        if image1:
            image_paths['image1'] = default_storage.save(f'product_variants/images/{product.id}/{image1.name}', image1)
        if image2:
            image_paths['image2'] = default_storage.save(f'product_variants/images/{product.id}/{image2.name}', image2)
        if image3:
            image_paths['image3'] = default_storage.save(f'product_variants/images/{product.id}/{image3.name}', image3)

        # Optionally, you could save these images to the ProductVariant model
        ProductVariant.objects.create(
            product=product,
            image1=image_paths.get('image1'),
            image2=image_paths.get('image2'),
            image3=image_paths.get('image3')
        )

        return JsonResponse({
            'success': True,
            'message': 'Images uploaded successfully.',
            **image_paths
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)