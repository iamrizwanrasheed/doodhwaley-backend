# Generated by Django 3.1.7 on 2021-09-14 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0045_remove_product_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='cancelledorder',
            name='status',
            field=models.CharField(blank=True, default='WAITING', max_length=20),
        ),
    ]