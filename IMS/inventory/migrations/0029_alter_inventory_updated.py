# Generated by Django 5.1.1 on 2024-09-09 16:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_alter_inventory_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 9, 21, 58, 23, 759050)),
        ),
    ]
