from django.db import models
from django.conf import settings
from products.models import Product,ProductVariant

# Create your models here.



# Wishlist Model

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='wishlist_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product_variant')

    def __str__(self):
        return f"{self.product_variant.product.name} in {self.user.username}'s Wishlist"