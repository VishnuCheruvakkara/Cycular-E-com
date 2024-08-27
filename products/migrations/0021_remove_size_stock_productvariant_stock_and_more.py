# Generated by Django 5.0.7 on 2024-08-25 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0020_remove_productvariant_color_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='size',
            name='stock',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='stock',
            field=models.PositiveIntegerField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='productvariant',
            unique_together={('size', 'product')},
        ),
    ]