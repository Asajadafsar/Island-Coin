# Generated by Django 5.0.7 on 2024-07-24 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Front', '0003_alter_inventory_fullcharge_alter_inventory_rocket'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='rocket_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inventory',
            name='rocket_multiplier',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='inventory',
            name='rocket_used',
            field=models.IntegerField(default=0),
        ),
    ]