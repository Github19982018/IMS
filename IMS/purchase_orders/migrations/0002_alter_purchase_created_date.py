# Generated by Django 5.1.1 on 2024-09-07 16:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase_orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 7, 22, 20, 49, 912051)),
        ),
    ]
