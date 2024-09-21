from django.contrib import admin
from coupon.models import Coupon,CouponUsage

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_value', 'valid_from', 'valid_until', 'active')
    list_filter = ('active', 'valid_from', 'valid_until')
    search_fields = ('code',)
    ordering = ('-valid_from',)

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'coupon', 'used_on', 'is_used')  # Display these fields in the admin list view
    search_fields = ('user__email', 'coupon__code')  # Add search functionality for user email and coupon code
    list_filter = ('is_used', 'used_on')