# Generated by Django 5.1.1 on 2024-11-18 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nails', '0014_contact_created_at_contact_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='social',
            field=models.CharField(choices=[('Facebook', 'Facebook'), ('Tiktok', 'Tiktok'), ('Instagram', 'Instagram'), ('Phone', 'Phone'), ('Location', 'Location')], max_length=50),
        ),
    ]