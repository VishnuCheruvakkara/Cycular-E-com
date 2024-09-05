from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

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

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='product_variants', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, related_name='size_variants', on_delete=models.CASCADE, null=True, blank=True)
    stock = models.PositiveIntegerField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image1 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='product_variants/images/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    class Meta:
        unique_together = ['size','product']

    def __str__(self):
        return f"{self.size.name} - {self.product.name}"  # Updated __str__ method

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"
                