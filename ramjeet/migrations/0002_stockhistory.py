# Generated by Django 5.0.7 on 2024-11-03 15:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ramjeet', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('previous_quantity', models.IntegerField(blank=True, null=True)),
                ('new_quantity', models.IntegerField(blank=True, null=True)),
                ('previous_expired_date', models.DateField(blank=True, null=True)),
                ('new_expired_date', models.DateField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ramjeet.inventorymaster')),
            ],
        ),
    ]
