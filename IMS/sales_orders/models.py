from bulkmodel.models import BulkModel
from django.db import models
from inventory.models import ShipMethod,Inventory
from customer.models import Customer
from warehouse.models import Warehouse
from datetime import datetime

# Create your models here.
class SalesStatus(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status

# class Purchase_draft(models.Model):
#     item = models.ForeignKey(to=)


class Sales(models.Model):
    warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
    sales_person = models.CharField(max_length=100)
    customer = models.ForeignKey(to=Customer,null=True,on_delete=models.PROTECT)
    bill_address = models.TextField()
    contact_phone = models.PositiveIntegerField(null=True)
    ship_address = models.TextField()
    ship_method = models.ForeignKey(to=ShipMethod,null=True,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=datetime.now)
    total_amount = models.DecimalField(decimal_places=2,max_digits=10,null=True)
    status = models.ForeignKey(to=SalesStatus,null=True,on_delete=models.PROTECT)
    updated = models.DateTimeField(default=datetime.now)


class  SalesItems(models.Model):
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE,related_name='items')
    item = models.ForeignKey(to=Inventory,null=True,related_name='sales',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    customer = models.ForeignKey(to=Customer,null=True,on_delete=models.PROTECT)
    @property
    def total_price(self):
        return self.quantity*self.price
    
class SaleItems(BulkModel):
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE)
    item = models.ForeignKey(to=Inventory,null=True,on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    customer = models.ForeignKey(to=Customer,null=True,on_delete=models.PROTECT)


class PackageStatus(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status

class ShipStatus(models.Model):
    id=models.SmallIntegerField(primary_key=True,default=1)
    status = models.CharField(max_length=50)
    def __str__(self) -> str:
        return self.status
class Shipment(models.Model):
    tracking_number = models.PositiveBigIntegerField(editable=False)
    created_at = models.DateTimeField(default=datetime.now)
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE,related_name='shipment')
    ship_method = models.ForeignKey(to=ShipMethod,on_delete=models.PROTECT)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    shipment_address = models.CharField(max_length=200)
    shipment_date = models.DateTimeField(null=True)
    status = models.ForeignKey(null=True,to=ShipStatus,on_delete=models.PROTECT)

class Package(models.Model):
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE,related_name='package')
    created_at = models.DateTimeField()
    packed_at = models.DateTimeField(null=True)
    shipping_address = models.CharField(max_length=200)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    status = models.ForeignKey(to=PackageStatus,on_delete=models.PROTECT)
    ship = models.ForeignKey(to=Shipment,on_delete=models.PROTECT,related_name='package')



