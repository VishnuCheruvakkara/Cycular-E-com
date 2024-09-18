from django.db import models
from django.conf import settings
from products.models import ProductVariant,Brand,Category
from django.utils import timezone
from django.core.validators import MinValueValidator

# Create your models here.

# Order Model
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'CASH ON DELIVERY'),
        ('razorpay', 'RAZORPAY'),
        ('wallet', 'WALLET'),
    ]

    ORDER_STATUS_CHOICES = [
    ('Pending', 'Pending'),               # Order has been placed but not yet processed
    ('Processing', 'Processing'),         # Order is being prepared or packaged
    ('Out for Delivery', 'Out for Delivery'), # Order is out for delivery to the customer
    ('Delivered', 'Delivered'),           # Order has been delivered to the customer
    ('Cancelled', 'Cancelled'),           # Order was cancelled by the customer or seller
    ('Refunded', 'Refunded'),             # Payment has been refunded to the customer
   
]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash_on_delivery')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_payment_method_display(self):
        # Convert PAYMENT_CHOICES to a dictionary
        choices_dict = dict(self.PAYMENT_CHOICES)
        return choices_dict.get(self.payment_method, self.payment_method)

    def get_order_status_display(self):
        # Convert ORDER_STATUS_CHOICES to a dictionary
        status_dict = dict(self.ORDER_STATUS_CHOICES)
        return status_dict.get(self.order_status, self.order_status)


# OrderItem Model
class OrderItem(models.Model):
    ORDER_STATUS_CHOICES = [
    ('Pending', 'Pending'),               # Order has been placed but not yet processed
    ('Processing', 'Processing'),         # Order is being prepared or packaged
    ('Out for Delivery','Out for Delivery'), # Order is out for delivery to the customer
    ('Delivered', 'Delivered'),           # Order has been delivered to the customer
    ('Cancelled', 'Cancelled'),           # Order was cancelled by the customer or seller
    ('Refunded', 'Refunded'),   
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    order_item_status = models.CharField(max_length=20,default='Pending', choices=ORDER_STATUS_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_variant.product.name} (x{self.quantity}) - Order {self.order.id}"

#address for the orderd products
# ...
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

