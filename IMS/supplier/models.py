from django.db import models

# Create your models here.
    
    
class Supplier_rating(models.Model):
    CHOICES = ((1,'Poor'),(2,'Fair'),(3,'Satisfactory'),(4,'Good'),(5,'Excellent'))
    competency = models.SmallIntegerField(choices=CHOICES)
    communication = models.SmallIntegerField(choices=CHOICES)
    commitment = models.SmallIntegerField(choices=CHOICES)
    transaction = models.SmallIntegerField(choices=CHOICES)
    consistency = models.SmallIntegerField(choices=CHOICES)
    cost = models.SmallIntegerField(choices=CHOICES)
    def total_rating(self):
        rate =  (self.competency + self.commitment + self.communication +self.transaction + self.consistency + self.cost)/6
        return round(rate,1)
        
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email  = models.EmailField(unique=True)
    phone = models.PositiveIntegerField()
    address = models.TextField()
    since = models.DateField()
    rating = models.OneToOneField(to=Supplier_rating,blank=True,null=True, on_delete=models.CASCADE,related_name='supplier')
    def __str__(self):
        return self.name