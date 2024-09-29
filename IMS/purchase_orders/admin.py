from django.contrib import admin
from purchase_orders.models import PurchaseStatus,ReceiveStatus

# Register your models here.
admin.site.register([PurchaseStatus,ReceiveStatus])