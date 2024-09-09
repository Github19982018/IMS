# Generated by Django 5.1.1 on 2024-09-09 16:36

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0006_alter_sales_created_date_alter_sales_total_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 22, 6, 25, 600593)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='sales_orders.sales_status'),
        ),
    ]
