from django.db import models
from django.conf import settings
from products.models import ProductVariant
from user_side.models import Address
# Create your models here.

# Order Model
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method=models.CharField(max_length=20,choices=[('cash_on_delivery','cash_on_delivery'),('razorpay','razorpay'),('wallet','wallet')],default='cash_on_delivery')
    payment_status = models.CharField(max_length=20,default='Pending' , choices=[('Pending', 'Pending'),('Paid', 'Paid'),('Failed', 'Failed'),])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(max_length=20,default='Pending' , choices=[('Pending', 'Pending'),('Paid', 'Paid'),('Failed', 'Failed'),])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_variant.product.name} (x{self.quantity}) - Order {self.order.id}"

#address for the orderd products...
class OrderAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE,related_name='order_address')
    address_line = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"Order {self.order.id} Address - {self.address_line}, {self.city}"







