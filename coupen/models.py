from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

# Create your models here.



#coupen model

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)]) 
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    description=models.CharField(max_length=250)
  
    def __str__(self):
        return f"Coupon {self.code} - {self.discount_value}% off"