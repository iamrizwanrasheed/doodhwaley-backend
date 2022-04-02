# Generated by Django 3.1.7 on 2021-07-24 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0028_onlinepayment_rechargehistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='onlinepayment',
            name='amount',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='onlinepayment',
            name='status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='onlinepayment',
            name='type_of',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]