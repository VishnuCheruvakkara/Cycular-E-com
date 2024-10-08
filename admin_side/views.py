from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from user_side.models import User 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
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
        admin_user = authenticate(request, email=email, password=password)
        if admin_user is not None:
            if admin_user.is_superuser:
                login(request, admin_user)
                return redirect('admin_side:seller-home')
            else:
                messages.error(request, "You don't have permission to access the admin panel.")
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'admin_side/admin_login.html')

#############################   seller logout  ########################################################

def SellerLogout(request):
    logout(request)
    return redirect('admin_side:seller-login')

#############################   user management  ########################################################

@login_required(login_url='admin_side:seller_login')
def UserManagement(request):

    customers=User.objects.filter(is_superuser=False)

    return render(request,'admin_side/user_management.html',{"customers":customers})

#############################   category management  ########################################################

