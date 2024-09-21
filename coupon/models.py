from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator
from django.contrib.auth import get_user_model

User = get_user_model()
# Create your models here.

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])  # Percentage value, should be between 0 and 100
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()
    description=models.CharField(max_length=250,null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        # Displaying the coupon code and discount percentage
        return f"Coupon {self.code} - {self.discount_value}% off"

    def save(self, *args, **kwargs):
        if self.valid_until:
            # If time is not specified, set the time to 12 PM (noon)
            if self.valid_until.hour == 0 and self.valid_until.minute == 0 and self.valid_until.second == 0:
                self.valid_until = self.valid_until.replace(hour=12, minute=0, second=0)
        super().save(*args, **kwargs)


# CouponUsage model to track usage of coupons by users
class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_on = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'coupon')  # Ensure a user can use a coupon only once

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


