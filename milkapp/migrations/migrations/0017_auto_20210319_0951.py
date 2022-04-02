# Generated by Django 3.1.7 on 2021-03-19 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0016_auto_20210319_0950'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliveryboynotifications',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='deliveryboynotifications',
            name='longitude',
        ),
        migrations.AddField(
            model_name='deliveryboy',
            name='zone_latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='deliveryboy',
            name='zone_longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]