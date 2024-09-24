from django.contrib import admin
from .models import Cart,CartItem

# Register your models here.


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_variant', 'quantity','subtotal','discount_amount','discounted_price')
    search_fields = ('cart__user__username', 'product_variant__product__name')
    list_filter = ('product_variant__product__category',)

