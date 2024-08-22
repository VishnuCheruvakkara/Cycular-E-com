from django.contrib import admin

# Register your models here.

from .models import Brand, Color, Size, Category, Product, ProductVariant, Review

from django.contrib import admin
from .models import Brand, Category, Product, Color, Size, ProductVariant, Review

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category' , 'status', 'created_at', 'updated_at')
    list_filter = ('brand', 'category', 'status')
    search_fields = ('name', 'description')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    list_filter = ('product',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'stock')
    list_filter = ('color',)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'get_color' , 'price' , 'image1' , 'image2', 'image3')
    list_filter = ('product', 'size__color')

    def get_color(self, obj):
        return obj.size.color.name if obj.size and obj.size.color else 'No Color'
    get_color.short_description = 'Color'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
