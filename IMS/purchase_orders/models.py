from django.db import models
from bulkmodel.models import BulkModel
from inventory.models import Supplier,ShipMethod,Inventory
from datetime import datetime
from warehouse.models import Warehouse


# Create your models here.
class Purchase_status(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status

# class Purchase_draft(models.Model):
#     item = models.ForeignKey(to=)

class PurchaseOrder(models.Model):
    warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=100)
    bill_address = models.TextField()
    contact_phone = models.PositiveIntegerField()
    ship_address = models.TextField()
    ship_method = models.ForeignKey(to=ShipMethod,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateTimeField()
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=datetime.now)
    total_amount = models.DecimalField(decimal_places=2,max_digits=10)
    status = models.ForeignKey(to=Purchase_status,on_delete=models.PROTECT)

class PurchaseReceive(models.Model):
    created_date = models.DateTimeField(default=datetime.now)
    order = models.OneToOneField(to=PurchaseOrder,related_name='order',on_delete=models.CASCADE)
    delivered_date = models.DateTimeField(null=True)
    status = models.ForeignKey(to=Purchase_status,on_delete=models.PROTECT)

class  PurchaseItems(models.Model):
    purchase = models.ForeignKey(to=PurchaseOrder,on_delete=models.CASCADE,related_name='items')
    item = models.ForeignKey(to=Inventory,related_name='purchase',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    supplier = models.ForeignKey(to=Supplier,null=True,on_delete=models.PROTECT)
    @property
    def total_price(self):
        return self.quantity*self.price
    
class PurchasesItems(BulkModel):
    purchase = models.ForeignKey(to=PurchaseOrder,on_delete=models.CASCADE,related_name='item')
    item = models.ForeignKey(to=Inventory,related_name='purchases',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    supplier = models.ForeignKey(to=Supplier,null=True,on_delete=models.PROTECT)
    @property
    def total_price(self):
        return self.quantity*self.price
    



