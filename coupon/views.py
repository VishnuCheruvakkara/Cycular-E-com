from django.shortcuts import render,redirect,get_object_or_404
from datetime import datetime
from .models import Coupon
from django.contrib import messages
import re
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.core.exceptions import ValidationError
from .validation import validate_coupon_data

############################  admin coupen page  ##########################

@login_required(login_url='admin_side:seller-login')
@never_cache
def coupon_management(request):
    add_errors = {}
    search_term = request.GET.get('search', '') 

    if request.method == 'POST' and 'add_coupon' in request.POST:
        add_errors, data = validate_coupon_data(request.POST)

        if not add_errors:
            coupon = Coupon(
                code=data['code'],
                discount_value=data['discount_value'],
                valid_until=data['valid_until'],
                description=data['description'],
                min_purchase_amount=data['min_purchase_amount'],
                max_discount_amount=data['max_discount_amount']
            )
            coupon.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('coupon:coupon-management')
        else:
            messages.error(request, 'There were errors in your Add Coupon form.')

    coupon_list = Coupon.objects.filter(active=True, valid_until__gte=timezone.now()).order_by('valid_until')
    if search_term:
        coupon_list = coupon_list.filter(code__icontains=search_term)

    paginator = Paginator(coupon_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'coupons': page_obj,
        'add_errors': add_errors,
        'old_data': {
            'code': request.POST.get('code', ''),
            'discount_value': request.POST.get('discount_value', ''),
            'valid_until': request.POST.get('valid_until', ''),
            'description': request.POST.get('description', ''),
            'min_purchase_amount': request.POST.get('min_purchase_amount', ''),
            'max_discount_amount': request.POST.get('max_discount_amount', ''),
        }
    }

    return render(request, 'coupon/coupon-management.html', context)


######################  edit button view function logic  ##########################

@login_required(login_url='admin_side:seller-login')
@never_cache
def edit_coupon(request, coupon_id):
    edit_errors = {}
    coupon = get_object_or_404(Coupon, id=coupon_id)

    if request.method == 'POST':
        edit_errors, data = validate_coupon_data(request.POST, coupon_id=coupon.id)

        if not edit_errors:
            coupon.code = data['code']
            coupon.discount_value = data['discount_value']
            coupon.valid_until = data['valid_until']
            coupon.description = data['description']
            coupon.min_purchase_amount = data['min_purchase_amount']
            coupon.max_discount_amount = data['max_discount_amount']
            coupon.save()

            messages.success(request, 'Coupon updated successfully!')
            return redirect('coupon:coupon-management')
        else:
            messages.error(request, 'There were errors in your Edit Coupon form.')
            edit_errors['coupon_id'] = coupon.id
           
    coupons = Coupon.objects.filter(active=True)
    context = {
        'coupon': coupon,
        'edit_errors': edit_errors,
        'coupons': coupons,
        'edit_coupon_id': edit_errors.get('coupon_id')
    }
    return render(request, 'coupon/coupon-management.html', context)


####################  soft delete for the created coupon  #########################

@login_required(login_url='admin_side:seller-login')
@never_cache
def delete_coupon(request, coupon_id):
    if request.method == 'POST':
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            
            # Soft delete the coupon by setting active to False
            coupon.active = False
            coupon.save()

            return JsonResponse({'success': True})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Coupon not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)