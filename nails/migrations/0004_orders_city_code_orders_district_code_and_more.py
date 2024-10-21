# Generated by Django 5.1.1 on 2024-10-07 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nails', '0003_remove_orders_total_payment_carts_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='city_code',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='district_code',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='orders',
            name='serial_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='orders',
            name='ward_code',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]