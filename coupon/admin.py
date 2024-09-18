from django.contrib import admin
from coupon.models import Coupon

# Register your models here.

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_value', 'valid_from', 'valid_until', 'active')
    list_filter = ('active', 'valid_from', 'valid_until')
    search_fields = ('code',)
    ordering = ('-valid_from',)