# Generated by Django 5.0.7 on 2024-08-19 07:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_alter_productvariant_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together={('product', 'size')},
        ),
    ]