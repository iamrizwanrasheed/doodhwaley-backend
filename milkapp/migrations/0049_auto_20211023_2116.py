# Generated by Django 3.1.7 on 2021-10-23 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0048_auto_20211014_0936'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='back_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='product',
            name='side_image',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
