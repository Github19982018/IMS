# Generated by Django 5.1.1 on 2024-09-30 04:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase_orders', '0010_receivestatus_rename_purchase_status_purchasestatus_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='cancel',
            field=models.BooleanField(default=False),
        ),
    ]
