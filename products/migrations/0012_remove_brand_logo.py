# Generated by Django 5.0.7 on 2024-08-22 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_category_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='brand',
            name='logo',
        ),
    ]
