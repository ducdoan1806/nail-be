# Generated by Django 5.1.1 on 2024-10-07 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nails', '0004_orders_city_code_orders_district_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='city_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='district_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='orders',
            name='ward_code',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
