from django.db import models
from bulkmodel.models import BulkModel
from inventory.models import Supplier,ShipMethod,Inventory
from datetime import datetime
from warehouse.models import Warehouse
from django.utils import timezone


# Create your models here.
class PurchaseStatus(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status
class ReceiveStatus(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status

class PurchaseDraft(models.Model):
    supplier = models.ForeignKey(to=Supplier,null=True,on_delete=models.PROTECT)

class PurchaseOrder(models.Model):
    id = models.OneToOneField(to=PurchaseDraft,on_delete=models.CASCADE,related_name='order',primary_key=True)
    warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=100)
    bill_address = models.TextField()
    contact_phone = models.PositiveIntegerField()
    ship_address = models.TextField()
    ship_method = models.ForeignKey(to=ShipMethod,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateTimeField(default=datetime.now)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField()
    updated = models.DateTimeField()
    total_amount = models.DecimalField(decimal_places=2,max_digits=10)
    status = models.ForeignKey(to=PurchaseStatus,on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_date = datetime.now()
        self.updated = datetime.now()
        return super(PurchaseOrder,self).save(*args,**kwargs)
    
    # def update(self, *args, **kwargs):
    #     self.updated = timezone.now()
    #     return super(PurchaseOrder,self).update(*args,**kwargs)
    

class PurchaseReceive(models.Model):
    updated = models.DateTimeField()
    created_date = models.DateTimeField(default=datetime.now)
    ref = models.OneToOneField(to=PurchaseDraft,related_name='receive',on_delete=models.CASCADE)
    delivered_date = models.DateTimeField(null=True)
    status = models.ForeignKey(to=ReceiveStatus,on_delete=models.PROTECT)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_date = datetime.now()
        self.updated = datetime.now()
        return super(PurchaseReceive,self).save(*args,**kwargs)
    
class  PurchaseItems(models.Model):
    purchase = models.ForeignKey(to=PurchaseDraft,on_delete=models.CASCADE,related_name='items')
    item = models.ForeignKey(to=Inventory,related_name='purchase',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    @property
    def total_price(self):
        return self.quantity*self.price
    
class PurchasesItems(BulkModel):
    purchase = models.ForeignKey(to=PurchaseDraft,on_delete=models.CASCADE,related_name='item')
    item = models.ForeignKey(to=Inventory,related_name='purchases',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    @property
    def total_price(self):
        return self.quantity*self.price
    



