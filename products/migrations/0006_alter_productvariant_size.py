# Generated by Django 5.0.7 on 2024-08-09 09:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_productvariant_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='size_variants', to='products.size'),
        ),
    ]
