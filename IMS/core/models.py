from django.db import models
from accounts.models import User
from datetime import datetime

# Create your models here.

class Notifications(models.Model):
    TAGS = (('info','information'),
            ('warning','warning'),
            ('success','success'),
            ('danger','danger'),
            ('primary','primary'))
    title = models.CharField(max_length=100)
    message = models.TextField(default='')
    tag = models.CharField(choices=TAGS,max_length=20)
    link = models.URLField(null=True)
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)
    user = models.ManyToManyField(to=User,related_name='notifications')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['-created',]

class Messages(models.Model):
    sender = models.ForeignKey(to=User,related_name='send_messages',on_delete=models.CASCADE)
    receivers = models.ManyToManyField(to=User,related_name='received_messages')
    message = models.TextField()
    seen = models.BooleanField(default=False)
    created = models.DateTimeField(default=datetime.now)


