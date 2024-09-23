from django.db import models
from products.models import Brand,ProductVariant
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class BrandOffer(models.Model):
    brand = models.ForeignKey(Brand, related_name='brand_offers', on_delete=models.CASCADE)
    offer_name = models.CharField(max_length=100)
    discount_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)] )  # e.g., 10% off
    start_date = models.DateField(auto_now_add=True) 
    end_date = models.DateField()
    status = models.BooleanField(default=True)  # Whether the offer is active or not

    def __str__(self):
        return f'{self.offer_name} - {self.brand.name}'


class ProductVariantOffer(models.Model):
    product_variant = models.ForeignKey(ProductVariant, related_name='variant_offers', on_delete=models.CASCADE)
    offer_name = models.CharField(max_length=100)
    discount_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])  # e.g., 15% off
    start_date = models.DateField(auto_now_add=True) 
    end_date = models.DateField()
    status = models.BooleanField(default=True)  # Offer active or not

    def __str__(self):
        return f'{self.offer_name} - {self.product_variant.product.name} ({self.product_variant.size.name})'


class ReferralOffer(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    usage_limit = models.IntegerField(default=1)
    start_date = models.DateField(auto_now_add=True) 
    end_date = models.DateField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'Referral Code: {self.code}'
