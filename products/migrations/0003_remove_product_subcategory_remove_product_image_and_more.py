# Generated by Django 5.0.7 on 2024-08-08 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_productvariant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='subcategory',
        ),
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='images',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='SubCategory',
        ),
    ]
