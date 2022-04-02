# Generated by Django 3.1.7 on 2021-08-23 08:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('milkapp', '0037_auto_20210823_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type_of',
            field=models.CharField(default='ALL', max_length=20),
        ),
        migrations.AlterField(
            model_name='storeareas',
            name='store_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='area', to='milkapp.store'),
        ),
    ]
