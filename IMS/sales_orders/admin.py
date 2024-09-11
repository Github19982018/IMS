from django.contrib import admin
from sales_orders.models import Sales_status,Ship_status
# Register your models here.
admin.site.register([Sales_status,Ship_status])