from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.
class User(AbstractUser):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=100)
    is_verified=models.BooleanField(default=False)
    date_joined=models.DateTimeField(default=timezone.now)
        
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username']

    def __str__(self):
        return self.username 


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20, blank=True, null=True) 
    is_default = models.BooleanField(default=False)  # Indicates the default address for a user

    def __str__(self):
        return f"{self.city}, {self.state} - {self.postal_code}"
