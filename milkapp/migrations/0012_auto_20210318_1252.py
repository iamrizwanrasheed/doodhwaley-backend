# Generated by Django 3.1.7 on 2021-03-18 12:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0011_auto_20210317_0816'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('CASH', 'CASH'), ('GATEWAY', 'GATEWAY')], default='CASH', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='milkapp.store'),
        ),
    ]
