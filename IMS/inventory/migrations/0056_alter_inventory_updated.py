# Generated by Django 5.1.1 on 2024-09-13 18:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0055_alter_inventory_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 14, 0, 4, 57, 102455)),
        ),
    ]
