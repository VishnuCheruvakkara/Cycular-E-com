# Generated by Django 5.0.7 on 2024-08-25 11:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_productvariant_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariant',
            name='color',
        ),
        migrations.AlterUniqueTogether(
            name='size',
            unique_together={('name',)},
        ),
        migrations.RemoveField(
            model_name='size',
            name='color',
        ),
        migrations.DeleteModel(
            name='Color',
        ),
    ]