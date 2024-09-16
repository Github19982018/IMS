from django.db import models
from datetime import datetime
from supplier.models import Supplier,Supplier_rating
from warehouse.models import Warehouse

# Create your models here.
class Category(models.Model):
    category = models.CharField(max_length=50)

class Brand(models.Model):
    brand = models.CharField(unique=True,max_length=50)


class Inventory(models.Model):
    photo = models.ImageField(null=True,blank=True,upload_to='items')
    name = models.CharField(unique=True, max_length=100)
    sku = models.CharField(unique=True,max_length=100)
    purchasing_price = models.DecimalField(decimal_places=2,max_digits=10)
    selling_price = models.DecimalField(decimal_places=2,max_digits=10)
    on_hand = models.PositiveIntegerField()
    description = models.TextField(blank=True,null=True)
    units = models.CharField(max_length=50,blank=True)
    dimensions = models.CharField(max_length=100)
    weight = models.PositiveIntegerField()
    updated = models.DateTimeField(default=datetime.now)
    brand = models.ForeignKey(to=Brand,blank=True,null=True,on_delete=models.CASCADE)
    warehouse = models.ManyToManyField(to=Warehouse,related_name='items')
    preferred_supplier = models.ForeignKey(to=Supplier,blank=True,null=True,on_delete=models.PROTECT)
    reorder_point = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.name


class ShipMethod(models.Model):
    method = models.CharField(max_length=50)

    def __str__(self):
        return self.method



# 
    









