# Generated by Django 5.1.1 on 2024-09-09 16:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0005_alter_sales_created_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sales',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 22, 2, 53, 119082)),
        ),
        migrations.AlterField(
            model_name='sales',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
    ]
