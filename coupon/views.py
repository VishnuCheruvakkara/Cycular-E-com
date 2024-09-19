from django.shortcuts import render,redirect,get_object_or_404
from datetime import datetime
from .models import Coupon
from django.contrib import messages
import re
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

# Create your views here.

############################  admin coupen page  ##########################

@login_required(login_url='admin_side:seller-login')
@never_cache
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
    
    coupon_list=Coupon.objects.filter(active=True)
    paginator = Paginator(coupon_list, 5)  # Show 10 coupons per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'coupons':page_obj,
        'errors':errors,
    }
   
    return render(request, 'coupon/coupon-management.html',context)


######################  edit button view function logic  ##########################


def edit_coupon(request, coupon_id):
    errors = {}
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        discount_value = request.POST.get('discount_value')
        valid_until_str = request.POST.get('valid_until')
        description = request.POST.get('description')

        # Field validations
        if not code:
            errors['code'] = "Coupon code is required."
        elif Coupon.objects.filter(code=code).exclude(id=coupon.id).exists():
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
                errors['valid_until'] = "The date cannot be a past date or current date."
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
            # Update coupon details
            coupon.code = code
            coupon.discount_value = discount_value
            coupon.valid_until = valid_until
            coupon.description = description
            coupon.save()

            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupon:coupon-management')  # Adjust to your actual view or URL
        else:
            messages.error(request, 'There were errors in your form.')
    coupons=Coupon.objects.filter(active=True)
    context = {
        'coupon': coupon,
        'errors': errors,
        'coupons':coupons,
    }
   
    return render(request, 'coupon/coupon-management.html', context)

####################  soft delete for the coupen  #########################

def delete_coupon(request, coupon_id):
    if request.method == 'POST':
        print(f"Received POST request to delete coupon {coupon_id}")
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            
            # Soft delete the coupon by setting active to False
            coupon.active = False
            coupon.save()

            return JsonResponse({'success': True})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Coupon not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)