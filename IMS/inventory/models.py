from django.db import models
from datetime import datetime
from supplier.models import Supplier,Supplier_rating

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    email  = models.EmailField(unique=True)
    phone = models.PositiveIntegerField()
    address = models.TextField()
    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100,null=True)
    contact_phone = models.PositiveIntegerField(null=True)
    def __str__(self):
        return self.name

class Category(models.Model):
    category = models.CharField(max_length=50)

class Brand(models.Model):
    brand = models.CharField(unique=True,max_length=50)

class Inventory(models.Model):
    photo = models.FilePathField(unique=True,null=True,blank=True)
    name = models.CharField(unique=True, max_length=100)
    sku = models.CharField(unique=True,max_length=100)
    purchasing_price = models.DecimalField(decimal_places=2,max_digits=10)
    selling_price = models.DecimalField(decimal_places=2,max_digits=10)
    on_hand = models.PositiveIntegerField()
    description = models.TextField()
    units = models.CharField(max_length=50,blank=True)
    updated = models.DateTimeField(default=datetime.now())
    brand = models.ForeignKey(to=Brand,null=True,on_delete=models.CASCADE)
    warehouse = models.ManyToManyField(to=Warehouse,related_name='warehouse')
    preferred_supplier = models.ForeignKey(to=Supplier,null=True,on_delete=models.PROTECT)
    reorder_point = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class Ship_method(models.Model):
    method = models.CharField(max_length=50)




# class Ship_status(models.Model):
#     status = models.CharField(max_length=50)

# class Shipment(models.Model):
#     # import random
#     # tracking_number = models.PositiveBigIntegerField()
#     sales = models.ManyToManyField(to=Sales)
#     created_at = models.DateTimeField()
#     sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE)
#     ship_method = models.ForeignKey(to=Ship_method,on_delete=models.PROTECT)
#     customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
#     shipment_address = models.CharField(max_length=200)
#     package = models.ForeignKey(to=Package,on_delete=models.CASCADE)
#     shipment_date = models.DateTimeField()
#     status = models.ForeignKey(to=Ship_status,on_delete=models.PROTECT)
    









