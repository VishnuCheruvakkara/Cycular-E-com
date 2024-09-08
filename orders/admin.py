from django.contrib import admin
from .models import Order,OrderItem

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'order_date', 'payment_method', 'payment_status', 'total_price')
    readonly_fields = ('order_date', 'total_price')
    list_filter = ('payment_status', 'payment_method', 'order_date')  # Ensure these fields exist

    def total_price(self, obj):
        return obj.total_price
    total_price.admin_order_field = 'total_price'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price', 'payment_status')
    list_filter = ('order__payment_status', 'order__order_date')  # Ensure these fields exist

    def price(self, obj):
        return obj.price
    price.admin_order_field = 'price'

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)