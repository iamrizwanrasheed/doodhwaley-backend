# Generated by Django 3.1.7 on 2021-07-24 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0029_auto_20210724_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinepayment',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]