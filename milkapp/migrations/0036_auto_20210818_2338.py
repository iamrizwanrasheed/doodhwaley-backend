# Generated by Django 3.1.7 on 2021-08-18 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0035_auto_20210818_1451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='category',
            new_name='subcategory',
        ),
    ]
