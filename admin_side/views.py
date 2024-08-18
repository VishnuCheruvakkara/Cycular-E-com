from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from user_side.models import User 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

# Create your views here.

#############################   seller home    ########################################################

@never_cache
@login_required(login_url='admin_side:seller-login')
def SellerHome(request):
    return render(request,'admin_side/admin_dashboard.html')

#############################   seller login  ########################################################

@never_cache
def SellerLogin(request):
    if request.user.is_authenticated:
        return redirect('admin_side:seller-home')
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.info(request,"Please fill the following...",extra_tags='admin')
            return render(request,'admin_side/admin_login.html')
        admin_user = authenticate(request, email=email, password=password)
        if admin_user is not None:
            if admin_user.is_superuser:
                login(request, admin_user)
                messages.success(request, "You have logged in successfully.", extra_tags='admin')
                return redirect('admin_side:seller-home')
            else:
                messages.error(request, "You don't have permission to access the admin panel.",extra_tags='admin')
        else:
            messages.error(request, "Invalid email or password.",extra_tags='admin')
    return render(request, 'admin_side/admin_login.html')

#############################   seller logout  ########################################################

def SellerLogout(request):
    logout(request)
    messages.success(request, 'You have logged out successfully',extra_tags='admin')
    return redirect('admin_side:seller-login')

#############################   user management  ########################################################

@login_required(login_url='admin_side:seller_login')
def UserManagement(request):

    customers=User.objects.filter(is_superuser=False)
   
    # Set up pagination.
    paginator = Paginator(customers, 5)  
    page = request.GET.get('page')
    try:
        customers_paginated = paginator.page(page)
    except PageNotAnInteger:
        customers_paginated = paginator.page(1)
    except EmptyPage:
        customers_paginated = paginator.page(paginator.num_pages)
    context={
        'customers':customers_paginated ,
        
    }
    return render(request,'admin_side/user_management.html',context)

#############################   category management  ########################################################

def UserView(request,user_id):
    user = get_object_or_404(User, id=user_id)
    context={
        'user':user
    }
    return render(request,'admin_side/user-view.html',context)
