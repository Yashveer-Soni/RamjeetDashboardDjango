# Generated by Django 5.0.7 on 2024-11-28 06:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ramjeet', '0008_deliveryaddress_full_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverymaster',
            name='delivery_date',
        ),
        migrations.RemoveField(
            model_name='shippingdetails',
            name='order',
        ),
        migrations.AddField(
            model_name='deliverymaster',
            name='shipping_detail',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ramjeet.shippingdetails'),
            preserve_default=False,
        ),
    ]
