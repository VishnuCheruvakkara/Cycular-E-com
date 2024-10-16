# Generated by Django 5.0.7 on 2024-10-03 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_alter_orderitem_order_item_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('Order placed', 'Order placed'), ('Payment Failed', 'Payment Failed'), ('Processing', 'Processing'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Refunded', 'Refunded')], default='Order placed', max_length=20),
        ),
    ]
