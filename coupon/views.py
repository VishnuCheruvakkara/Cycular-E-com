from django.shortcuts import render

# Create your views here.

def coupon_management(request):
    
    return render(request,'coupon/coupon-management.html')