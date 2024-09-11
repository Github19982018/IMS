from bulkmodel.models import BulkModel
from django.db import models
from inventory.models import Warehouse,Customer,Ship_method,Inventory
from datetime import datetime

# Create your models here.
class Sales_status(models.Model):
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
    ship_method = models.ForeignKey(to=Ship_method,null=True,on_delete=models.PROTECT)
    preferred_shipping_date = models.DateTimeField(null=True)
    created_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=datetime.now())
    total_amount = models.DecimalField(decimal_places=2,max_digits=10,null=True)
    status = models.ForeignKey(to=Sales_status,null=True,on_delete=models.PROTECT)


class  Sales_items(models.Model):
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE,related_name='items')
    item_id = models.ForeignKey(to=Inventory,null=True,related_name='sales',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    customer = models.ForeignKey(to=Customer,null=True,on_delete=models.PROTECT)
    @property
    def total_price(self):
        return self.quantity*self.price
    
class Sale_items(BulkModel):
    sales = models.ForeignKey(to=Sales,on_delete=models.CASCADE)
    item_id = models.ForeignKey(to=Inventory,null=True,on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    customer = models.ForeignKey(to=Customer,null=True,on_delete=models.PROTECT)


class Package_status(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    status = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.status


class Package(models.Model):
    slip = models.PositiveIntegerField(auto_created=True)
    sales = models.ManyToManyField(to=Sales)
    created_at = models.DateTimeField()
    packed_at = models.DateTimeField()
    shipping_address = models.CharField(max_length=200)
    customer = models.ForeignKey(to=Customer,on_delete=models.PROTECT)
    status = models.ForeignKey(to=Package_status,on_delete=models.PROTECT)