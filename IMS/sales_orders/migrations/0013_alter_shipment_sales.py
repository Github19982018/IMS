# Generated by Django 5.1.1 on 2024-10-05 19:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0012_shipment_cancel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='sales',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipment', to='sales_orders.sales'),
        ),
    ]
