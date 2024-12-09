# Generated by Django 5.0.7 on 2024-11-27 16:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ramjeet', '0005_customermaster_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True)),
                ('phoneNumber', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=20)),
                ('country', models.CharField(max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_addresses', to='ramjeet.customermaster')),
            ],
            options={
                'verbose_name': 'Delivery Address',
                'verbose_name_plural': 'Delivery Addresses',
            },
        ),
        migrations.AddField(
            model_name='ordermaster',
            name='delivery_address',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ramjeet.deliveryaddress'),
            preserve_default=False,
        ),
    ]
