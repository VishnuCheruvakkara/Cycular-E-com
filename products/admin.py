from django.contrib import admin
from .models import Brand, Category, Product, Size, ProductVariant, Review

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

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'price', 'image1', 'image2', 'image3','stock')
    list_filter = ('product', 'size')  # Removed color-related filter

    def get_color(self, obj):
        # Removed as color field no longer exists
        return 'No Color'
    get_color.short_description = 'Color'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
