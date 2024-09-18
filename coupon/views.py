from django.shortcuts import render,redirect
from datetime import datetime
from coupon.models import Coupon
from django.contrib import messages
import re

# Create your views here.

def coupon_management(request):
    errors = {}
    
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_value = request.POST.get('discount_value')
        valid_until_str = request.POST.get('valid_until')
        description = request.POST.get('description')

        # Field validations
        if not code:
            errors['code'] = "Coupon code is required."
        elif Coupon.objects.filter(code=code).exists():
            errors['code'] = "Coupon code already exists."

        if not discount_value:
            errors['discount_value'] = "Discount value is required."
        else:
            try:
                discount_value = float(discount_value)
                if discount_value < 0 or discount_value > 100:
                    errors['discount_value'] = "Discount value must be between 0 and 100."
            except ValueError:
                errors['discount_value'] = "Discount value must be a number."

        try:
            valid_until = datetime.strptime(valid_until_str, '%d-%m-%Y')
            if valid_until <= datetime.now():
                errors['valid_until']="The date cannot be the past date or current date."
        except ValueError:
            errors['valid_until'] = "Please enter a valid date in the format DD-MM-YYYY."

         # Alphanumeric validation for description
        if description:
            if not re.match(r'^[a-zA-Z0-9\s]+$', description):
                errors['description'] = "Description can only contain letters, numbers, and spaces."
        else:
            errors['description'] = "Description is required."
        # Proceed if no errors
        if not errors:
            coupon = Coupon(
                code=code,
                discount_value=discount_value,
                valid_until=valid_until,
                description=description,
            )
            coupon.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupon:coupon-management')  # Adjust to your actual view or URL
        else:
            messages.error(request, 'There were errors in your form.')
    coupons=Coupon.objects.all()
    context={
        'coupons':coupons,
        'errors':errors,
    }
   
    return render(request, 'coupon/coupon-management.html',context)
