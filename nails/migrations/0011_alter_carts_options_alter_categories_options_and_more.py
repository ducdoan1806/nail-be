# Generated by Django 5.1.1 on 2024-10-17 04:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nails', '0010_remove_district_province_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='carts',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='categories',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='orders',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'ordering': ['-id']},
        ),
        migrations.AlterField(
            model_name='products',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='nails.categories'),
        ),
    ]
