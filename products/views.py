from django.shortcuts import render,redirect
from .forms import ProductForm
from django.contrib import messages
from django.conf import settings
# Create your views here.

###################### Category Management page #################################

def CategoryManagement(request):
    return render(request,'products/category-management.html')

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

def EditProduct(request):
    return render(request,'products/edit-product.html')

