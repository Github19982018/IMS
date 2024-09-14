from django.db import models

# Create your models here.
class Warehouse(models.Model):
    name = models.CharField(max_length=100,unique=True)
    address = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100,null=True)
    contact_phone = models.PositiveIntegerField(null=True)
    def __str__(self):
        return self.name