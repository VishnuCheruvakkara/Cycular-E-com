from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator

# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2,validators=[MinValueValidator(0), MaxValueValidator(100)])  # Percentage value, should be between 0 and 100
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    description=models.CharField(max_length=250,null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        # Displaying the coupon code and discount percentage
        return f"Coupon {self.code} - {self.discount_value}% off"
