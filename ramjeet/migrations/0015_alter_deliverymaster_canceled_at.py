# Generated by Django 5.0.7 on 2024-11-28 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ramjeet', '0014_deliverymaster_canceled_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverymaster',
            name='canceled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]