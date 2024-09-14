from django.contrib import admin
from inventory import models

# Register your models here.
admin.site.register([models.Brand,models.ShipMethod])