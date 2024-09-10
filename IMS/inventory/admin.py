from django.contrib import admin
from inventory import models

# Register your models here.
admin.site.register([models.Brand,models.Ship_method,models.Ship_status,models.Package_status,models.Warehouse,models.Customer])