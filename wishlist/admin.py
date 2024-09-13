from django.contrib import admin
from .models import Wishlist

# Register your models here.

# Define admin classes for better customization if needed

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_variant', 'created_at')  # Displays these fields in the admin list view
    search_fields = ('user__username', 'product_variant__product__name')  # Enables search by user and product name
    list_filter = ('created_at',)  # Adds a filter sidebar for creation date