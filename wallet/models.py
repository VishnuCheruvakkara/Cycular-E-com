from django.db import models
from django.conf import settings

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # Assuming you're using the default User model

# Wallet Model
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

# Transaction Model
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )

    TRANSACTION_PURPOSES = (
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_purpose = models.CharField(max_length=10, choices=TRANSACTION_PURPOSES)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} for {self.transaction_purpose} "

                                      