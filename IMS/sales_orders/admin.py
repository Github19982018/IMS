from django.contrib import admin
from sales_orders.models import SalesStatus,ShipStatus
# Register your models here.
admin.site.register([SalesStatus,ShipStatus])