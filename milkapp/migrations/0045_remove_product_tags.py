# Generated by Django 3.1.7 on 2021-09-14 18:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0044_auto_20210914_2326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tags',
        ),
    ]
