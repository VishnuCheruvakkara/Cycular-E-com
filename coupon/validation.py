from .models import Coupon
from datetime import datetime
import re


def validate_coupon_data(data, coupon_id=None):
    errors = {}
    cleaned_data = {}

    code = data.get('code', '').strip()
    discount_value = data.get('discount_value')
    valid_until_str = data.get('valid_until')
    description = data.get('description', '').strip()
    min_purchase_amount = data.get('min_purchase_amount')
    max_discount_amount = data.get('max_discount_amount')

    # ---------- Coupon Code ----------
    if not code:
        errors['code'] = "Coupon code is required."
    elif not re.match(r'^[A-Za-z0-9!@#$%^&*]+$', code):
        errors['code'] = "Coupon code can contain only letters, numbers, and special characters."
    else:
        qs = Coupon.objects.filter(code=code)
        if coupon_id:
            qs = qs.exclude(id=coupon_id)
        if qs.exists():
            errors['code'] = "Coupon code already exists."
        else:
            cleaned_data['code'] = code

    # ---------- Discount Value ----------
    try:
        discount_value = int(discount_value)
        if not (1 <= discount_value <= 99):
            errors['discount_value'] = "Discount value must be between 1 and 99."
        else:
            cleaned_data['discount_value'] = discount_value
    except (TypeError, ValueError):
        errors['discount_value'] = "Discount value must be a number."

    # ---------- Valid Until ----------
    try:
        valid_until = datetime.strptime(valid_until_str, '%d-%m-%Y')
        if valid_until.date() <= datetime.now().date():
            errors['valid_until'] = "Expiry date must be a future date."
        else:
            cleaned_data['valid_until'] = valid_until
    except (TypeError, ValueError):
        errors['valid_until'] = "Enter date in DD-MM-YYYY format."

    # ---------- Description ----------
    if not description:
        errors['description'] = "Description is required."
    elif not re.match(r'^[a-zA-Z0-9\s]+$', description):
        errors['description'] = "Description can only contain letters, numbers, and spaces."
    elif not re.search(r'[A-Za-z]',description):
        errors['description']="Description must contain at least one letter."
    else:
        cleaned_data['description'] = description

    # ---------- Minimum Purchase ----------
    try:
        min_purchase_amount = int(min_purchase_amount)
        if min_purchase_amount < 1:
            errors['min_purchase_amount'] = "Minimum purchase amount must be at least 1."
        else:
            cleaned_data['min_purchase_amount'] = min_purchase_amount
    except (TypeError, ValueError):
        errors['min_purchase_amount'] = "Minimum purchase amount must be a number."

    # ---------- Maximum Discount ----------
    try:
        max_discount_amount = int(max_discount_amount)
        if max_discount_amount < 1:
            errors['max_discount_amount'] = "Maximum discount amount must be at least 1."
        else:
            cleaned_data['max_discount_amount'] = max_discount_amount
    except (TypeError, ValueError):
        errors['max_discount_amount'] = "Maximum discount amount must be a number."

    # ---------- Cross-field Validation ----------
    if (
        'min_purchase_amount' in cleaned_data and
        'max_discount_amount' in cleaned_data
    ):
        if cleaned_data['max_discount_amount'] > cleaned_data['min_purchase_amount']:
            errors['max_discount_amount'] = (
                "Maximum discount cannot exceed minimum purchase amount."
            )

    return errors, cleaned_data
