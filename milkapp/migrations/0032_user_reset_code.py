# Generated by Django 3.1.7 on 2021-08-03 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0031_auto_20210729_0151'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_code',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]
