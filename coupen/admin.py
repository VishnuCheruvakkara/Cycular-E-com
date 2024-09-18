from django.contrib import admin
from .models import Coupon

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_value', 'valid_from', 'valid_to', 'active')  # Columns to display
    list_filter = ('active', 'valid_from', 'valid_to')  # Filter options in the sidebar
    search_fields = ('code',)  # Search bar for coupon codes