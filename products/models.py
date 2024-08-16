from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class Brand(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='brands', null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    key_specification = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    color = models.ForeignKey(Color, related_name='sizes', on_delete=models.CASCADE,null=True,blank=True)
   

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='product_variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='size_variants', on_delete=models.CASCADE,null=True, blank=True)
    image1 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)

    def __str__(self):
        product_name = getattr(self.size.color.product, 'name', 'No Product') if self.size and self.size.color and self.size.color.product else 'No Product'
        color_name = getattr(self.size.color, 'name', 'No Color') if self.size and self.size.color else 'No Color'
        size_name = getattr(self.size, 'name', 'No Size') if self.size else 'No Size'
        return f"{product_name} - {color_name} - {size_name}"

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
