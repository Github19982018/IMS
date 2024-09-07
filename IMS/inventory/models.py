from django.db import models
from datetime import date,datetime
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
    warehouse = models.ManyToManyField(to=Warehouse,null=True,related_name='warehouse')
    preferred_supplier = models.ForeignKey(to=Supplier,null=True,on_delete=models.PROTECT)
    reorder_point = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.name


class Ship_method(models.Model):
    method = models.CharField(max_length=50)
class Purchase_status(models.Model):
    status = models.CharField(max_length=50)

class Purchase(models.Model):
    Warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
    supplier = models.ForeignKey(to=Supplier,on_delete=models.PROTECT)
    contact_person = models.CharField(max_length=100)
    bill_address = models.TextField()
    contact_phone = models.PositiveIntegerField()
    ship_address = models.TextField()
    ship_method = models.ForeignKey(to=Ship_method,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateField()
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=datetime.now())
    total_amount = models.DecimalField(decimal_places=2,max_digits=10)
    status = models.ForeignKey(to=Purchase_status,on_delete=models.PROTECT)

class Sales_status(models.Model):
    status = models.CharField(max_length=50)

class Sales(models.Model):
    Warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
    responsible_person = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    bill_address = models.TextField()
    contact_phone = models.PositiveIntegerField()
    ship_address = models.TextField()
    ship_method = models.ForeignKey(to=Ship_method,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateField()
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(datetime.now)
    total_amount = models.DecimalField(decimal_places=2,max_digits=10)
    status = models.ForeignKey(to=Sales_status,on_delete=models.PROTECT)

class Package_status(models.Model):
    status = models.CharField(max_length=50)

class Package(models.Model):
    slip = models.PositiveIntegerField(auto_created=True)
    sales = models.ManyToManyField(to=Sales)
    created_at = models.DateTimeField()
    packed_at = models.DateTimeField()
    shipping_address = models.CharField(max_length=200)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    status = models.ForeignKey(to=Package_status,on_delete=models.PROTECT)

class Ship_status(models.Model):
    status = models.CharField(max_length=50)

class Shipment(models.Model):
    # import random
    # tracking_number = models.PositiveBigIntegerField()
    sales = models.ManyToManyField(to=Sales)
    created_at = models.DateTimeField()
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE)
    ship_method = models.ForeignKey(to=Ship_method,on_delete=models.PROTECT)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    shipment_address = models.CharField(max_length=200)
    package = models.ForeignKey(to=Package,on_delete=models.CASCADE)
    shipment_date = models.DateTimeField()
    status = models.ForeignKey(to=Ship_status,on_delete=models.PROTECT)

class  Order_items(models.Model):
    type = models.CharField(choices={'P':'Purchase','O':'Order'},max_length=20)
    order = models.ForeignKey(to=Purchase or Sales,on_delete=models.CASCADE)
    item_id = models.ManyToManyField(to=Inventory)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.PositiveIntegerField()
    @property
    def total_price(self):
        return self.quantity*self.price









