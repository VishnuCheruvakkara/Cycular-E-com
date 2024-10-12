from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    key_specification = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    # Removed 'color' reference and unique_together constraint
    class Meta:
        unique_together = ['name']

    def __str__(self):
        return self.name

class Color(models.Model):
    
    hex_code = models.CharField(max_length=20, unique=True, default='Not selected')
    name = models.CharField(max_length=50, unique=True)  # Ensure each color name is unique
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='product_variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, related_name='color_variants', on_delete=models.CASCADE, null=True, blank=True)
    size = models.ForeignKey(Size, related_name='size_variants', on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image1 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ['size','color','product']

    def __str__(self):
        return f"{self.size.name} - {self.product.name}"  # Updated __str__ method
    def get_discounted_price(self):
        """Calculate the discounted price based on product variant and brand offers."""
        from offer.models import ProductVariantOffer, BrandOffer  # Lazy import to avoid circular dependency 
       
        product_variant_offer = ProductVariantOffer.objects.filter(product_variant=self, status=True).first()
        brand_offer = BrandOffer.objects.filter(brand=self.product.brand, status=True).first()
        
        original_price = self.price
        variant_discount_percentage = Decimal(0)  # Default to 0 if no product variant offer
        brand_discount_percentage = Decimal(0)  # Default to 0 if no brand offer
        
        # Calculate product variant discount percentage
        if product_variant_offer:
            variant_discount_percentage = Decimal(product_variant_offer.discount_percentage)
        
        # Calculate brand discount percentage
        if brand_offer:
            brand_discount_percentage = Decimal(brand_offer.discount_percentage)
        
        # Determine the maximum discount percentage
        max_discount_percentage = max(variant_discount_percentage, brand_discount_percentage)
        
        # Calculate the discounted price
        discounted_price = original_price * (1 - (max_discount_percentage / Decimal(100)))
        
        return discounted_price

    def get_discount_percentage(self):
        """Return the maximum discount percentage applied to the product variant."""
        from offer.models import ProductVariantOffer, BrandOffer  # Lazy import to avoid circular dependency
        product_variant_offer = ProductVariantOffer.objects.filter(product_variant=self, status=True).first()
        brand_offer = BrandOffer.objects.filter(brand=self.product.brand, status=True).first()
        
        variant_discount_percentage = Decimal(0)
        brand_discount_percentage = Decimal(0)
        
        if product_variant_offer:
            variant_discount_percentage = Decimal(product_variant_offer.discount_percentage)
        
        if brand_offer:
            brand_discount_percentage = Decimal(brand_offer.discount_percentage)
        
        return max(variant_discount_percentage, brand_discount_percentage)
    
    def get_savings_amount(self):
        """Calculate how much the user is saving based on the applied discount."""
        original_price = self.price
        discounted_price = self.get_discounted_price()
        
        savings = original_price - discounted_price
        return savings
    

class Review(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product_variant', 'user')  # Prevent multiple reviews for the same product by the same user

    def __str__(self):
        return f"Review for {self.product_variant.product.name} by {self.user.username}"