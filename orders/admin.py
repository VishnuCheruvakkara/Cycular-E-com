from django.contrib import admin
from .models import Order, OrderItem, OrderAddress

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'payment_method', 'order_status', 'total_price','coupon_discount_total')
    list_filter = ('payment_method', 'order_status', 'order_date')
    search_fields = ('user__username', 'payment_method', 'order_status')
    ordering = ('-order_date',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price', 'order_item_status','coupon_disount_price')
    list_filter = ('order_item_status',)
    search_fields = ('order__id', 'product_variant__product__name')
    ordering = ('order',)

@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'address_line', 'city', 'state', 'country', 'postal_code', 'phone_number')
    search_fields = ('order__id', 'city', 'state', 'country')
    ordering = ('order',)

