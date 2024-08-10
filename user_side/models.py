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


