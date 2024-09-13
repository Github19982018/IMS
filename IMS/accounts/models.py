from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
# Create your models here.

class User(AbstractUser):
    USER_TYPE = ((1,"Inventory Manager"),
                 (2,"Inventory Specialist"))
    user_type = models.PositiveSmallIntegerField(null=True,choices=USER_TYPE)

class Manager(models.Model):
    manager_id = models.ForeignKey(User,on_delete=models.CASCADE,related_name='manager')
    phone = models.IntegerField(null=True)
    address = models.CharField(null=True,max_length=300)
    profile_photo = models.ImageField(upload_to='documents',blank=True)

class Specialist(models.Model):
    specialist_id = models.ForeignKey(User,on_delete=models.CASCADE,related_name='specialist')
    phone = models.IntegerField(null=True)
    address = models.CharField(null=True,max_length=300)
    profile_photo = models.ImageField(upload_to='documents',blank=True)
