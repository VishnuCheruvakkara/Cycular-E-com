# Generated by Django 5.0.7 on 2024-09-29 04:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0024_remove_productvariant_offer_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='color_variants', to='products.color'),
        ),
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together={('size', 'color', 'product')},
        ),
    ]
