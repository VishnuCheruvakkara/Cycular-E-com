from django.contrib import admin
from .models import Order, OrderItem, OrderAddress,Coupon

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'payment_method', 'order_status', 'total_price')
    list_filter = ('payment_method', 'order_status', 'order_date')
    search_fields = ('user__username', 'payment_method', 'order_status')
    ordering = ('-order_date',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price', 'order_item_status')
    list_filter = ('order_item_status',)
    search_fields = ('order__id', 'product_variant__product__name')
    ordering = ('order',)

@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'address_line', 'city', 'state', 'country', 'postal_code', 'phone_number')
    search_fields = ('order__id', 'city', 'state', 'country')
    ordering = ('order',)



@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'active')
    list_filter = ('discount_type', 'active', 'valid_from', 'valid_to')
    search_fields = ('code', 'discount_type', 'discount_value')
    ordering = ('-valid_from',)  # Show the most recent coupons first

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optionally: add more filtering or customization here
        return qs

    def has_change_permission(self, request, obj=None):
        # Optionally: customize permissions
        return super().has_change_permission(request, obj)
    
    def save_model(self, request, obj, form, change):
        # Optionally: add custom save logic
        super().save_model(request, obj, form, change)

