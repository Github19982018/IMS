# Generated by Django 5.1.1 on 2024-09-15 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales_orders', '0003_saleitems_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleitems',
            name='customer',
        ),
        migrations.AlterField(
            model_name='saleitems',
            name='discount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sales',
            name='offer',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='salesitems',
            name='discount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
