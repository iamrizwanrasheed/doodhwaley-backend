# Generated by Django 3.1.7 on 2021-03-21 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0020_auto_20210320_1331'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='quantity',
            field=models.CharField(default='1L', max_length=10),
        ),
    ]
