# Generated by Django 5.1.1 on 2024-09-07 16:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_rename_order_items_sale_items_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 7, 22, 20, 49, 900599)),
        ),
    ]
