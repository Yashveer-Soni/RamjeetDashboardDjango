# Generated by Django 5.0.7 on 2024-11-27 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ramjeet', '0007_remove_ordermaster_delivery_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryaddress',
            name='full_name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]