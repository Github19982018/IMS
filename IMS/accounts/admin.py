from django.contrib import admin
from accounts.models import User,Manager,Specialist

# Register your models here.
admin.site.register([User,Manager,Specialist])