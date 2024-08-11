from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm
from django.contrib import messages
from django.conf import settings
from .models import Product

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