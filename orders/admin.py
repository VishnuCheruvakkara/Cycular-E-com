from django.contrib import admin
from .models import Order,OrderItem

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'created_at', 'status', 'total_price')
    search_fields = ('user__username', 'address__address_line1')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'total_price')  # Prevent modification of these fields

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price')
    search_fields = ('order__user__username', 'product_variant__product__name')
    list_filter = ('order__status', 'product_variant__product__category')