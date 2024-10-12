from django.contrib import admin
from .models import Brand, Category, Product, Size,Color,ProductVariant

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'status', 'created_at', 'updated_at')
    list_filter = ('brand', 'category', 'status')
    search_fields = ('name', 'description')

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name','status')
    # Removed color-related fields and filters


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name','hex_code','status')  # Display name and status in the admin list view
    search_fields = ('name',)  # Add a search box for color name
    list_filter = ('status',)  # Filter by status in the admin interface

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size','color','price', 'image1', 'image2', 'image3','stock')
    list_filter = ('product', 'size')  # Removed color-related filter

