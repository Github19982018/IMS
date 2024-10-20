# Generated by Django 5.1.1 on 2024-09-14 06:40

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0001_initial'),
        ('supplier', '0007_remove_supplier_supplier_supplier_rating'),
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Purchase_status',
            fields=[
                ('id', models.SmallIntegerField(primary_key=True, serialize=False)),
                ('status', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_person', models.CharField(max_length=100)),
                ('bill_address', models.TextField()),
                ('contact_phone', models.PositiveIntegerField()),
                ('ship_address', models.TextField()),
                ('preferred_shipping_date', models.DateTimeField()),
                ('created_by', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(default=datetime.datetime.now)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ship_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.shipmethod')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchase_orders.purchase_status')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('units', models.CharField(max_length=50)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchase', to='inventory.inventory')),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='supplier.supplier')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='purchase_orders.purchaseorder')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseReceive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=datetime.datetime.now)),
                ('delivered_date', models.DateTimeField(null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order', to='purchase_orders.purchaseorder')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchase_orders.purchase_status')),
            ],
        ),
        migrations.CreateModel(
            name='PurchasesItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bm_create_uuid', models.UUIDField(db_index=True, default=None, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('units', models.CharField(max_length=50)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='inventory.inventory')),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item', to='purchase_orders.purchaseorder')),
                ('supplier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='supplier.supplier')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
