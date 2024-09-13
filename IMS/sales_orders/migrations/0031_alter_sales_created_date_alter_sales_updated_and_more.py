# Generated by Django 5.1.1 on 2024-09-13 18:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0030_alter_sales_created_date_alter_sales_updated_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 14, 0, 5, 53, 57651)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 14, 0, 5, 53, 57651)),
        ),
        migrations.AlterField(
            model_name='shipment',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 14, 0, 5, 53, 60438)),
        ),
    ]
