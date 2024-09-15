from django.contrib import admin
from sales_orders.models import SalesStatus,ShipStatus,PackageStatus
# Register your models here.
admin.site.register([SalesStatus,ShipStatus,PackageStatus])