# Generated by Django 5.0.7 on 2024-09-21 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_order_coupon_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='coupon_info',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='coupon_info',
            field=models.CharField(default='Not Available', max_length=250),
        ),
    ]
