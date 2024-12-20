# Generated by Django 5.0.7 on 2024-09-20 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_delete_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon_discount_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='coupon_disount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
