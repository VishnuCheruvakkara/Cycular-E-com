from django.contrib import admin
from .models import ProductVariantOffer, ReferralOffer

# Register your models here.


# Register ProductVariantOffer
@admin.register(ProductVariantOffer)
class ProductVariantOfferAdmin(admin.ModelAdmin):
    list_display = ('offer_name', 'product_variant', 'discount_percentage', 'start_date', 'end_date', 'status')
    search_fields = ('offer_name', 'product_variant__product__name')
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-start_date',)

# Register ReferralOffer
@admin.register(ReferralOffer)
class ReferralOfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'usage_limit', 'start_date', 'end_date', 'status')
    search_fields = ('code',)
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-start_date',)
