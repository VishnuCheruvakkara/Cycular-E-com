# Generated by Django 5.0.7 on 2024-09-19 05:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0003_rename_valid_to_coupon_valid_until_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='discount_value',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]