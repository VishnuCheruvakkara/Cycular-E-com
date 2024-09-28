# Generated by Django 5.0.7 on 2024-09-27 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0018_alter_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order_item_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Out for Delivery', 'Out for Delivery'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Return Requested', 'Return Requested'), ('Returned', 'Returned')], default='Pending', max_length=20),
        ),
    ]
