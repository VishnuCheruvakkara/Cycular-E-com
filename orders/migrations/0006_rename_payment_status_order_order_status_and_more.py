# Generated by Django 5.0.7 on 2024-09-08 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_payment_method'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='payment_status',
            new_name='order_status',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='payment_status',
            new_name='order_item_status',
        ),
    ]