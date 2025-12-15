from django.db import models
from django.conf import settings
from products.models import ProductVariant
from decimal import Decimal

# Create your models here.


# Cart Model
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"


# CartItem Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
  
    def __str__(self):
        return f"{self.product_variant.product.name} (x{self.quantity})"
    
    @property
    def discounted_price(self):
        discounted = self.product_variant.get_discounted_price()
        return discounted if discounted < self.product_variant.price else self.product_variant.price

    @property
    def discount_amount(self):
        discounted = self.product_variant.get_discounted_price()
        if discounted < self.product_variant.price:
            return (self.product_variant.price - discounted) * self.quantity
        return Decimal('0.00')

    @property
    def subtotal(self):
        return self.discounted_price * self.quantity