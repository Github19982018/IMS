from django.db import models
from inventory.models import Warehouse,Supplier,Ship_method,Inventory
from datetime import datetime

# Create your models here.
class Purchase_status(models.Model):
    status = models.CharField(max_length=50)

# class Purchase_draft(models.Model):
#     item = models.ForeignKey(to=)
class  Purchase_items(models.Model):
    type = models.CharField(choices={'P':'Purchase','O':'Order'},max_length=20)
    item_id = models.OneToOneField(to=Inventory,null=True,related_name='items',on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2,max_digits=10)
    quantity = models.PositiveIntegerField()
    units = models.CharField(max_length=50)
    @property
    def total_price(self):
        return self.quantity*self.price
class Purchase(models.Model):
    id = models.OneToOneField(to=Purchase_items,primary_key=True,on_delete=models.CASCADE)
    warehouse = models.ForeignKey(to=Warehouse,on_delete=models.CASCADE)
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
