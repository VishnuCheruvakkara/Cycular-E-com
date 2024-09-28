# Generated by Django 5.0.7 on 2024-09-28 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0023_alter_orderitem_cancelled_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order_item_status',
            field=models.CharField(choices=[('Order placed', 'Order placed'), ('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return Requested', 'Return Requested'), ('Returned', 'Returned')], default='Order placed', max_length=20),
        ),
    ]
