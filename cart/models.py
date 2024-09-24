from django.db import models
from django.conf import settings
from products.models import ProductVariant

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
    quantity = models.PositiveIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.product_variant.product.name} (x{self.quantity})"
    
    def save(self, *args, **kwargs):
        # Automatically update the subtotal whenever the cart item is saved
        self.subtotal = self.quantity * float(self.product_variant.price)
        super().save(*args, **kwargs)