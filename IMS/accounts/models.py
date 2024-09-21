from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
from django.core.mail import send_mail
from django.contrib.auth.validators import ASCIIUsernameValidator
from django.utils.translation import gettext_lazy as _
# Create your models here.

class User(AbstractUser):
    username_validator = ASCIIUsernameValidator
    USER_TYPE = ((2,"Inventory Manager"),
                 (3,"Inventory Specialist"),
                 (1,'admin'))
    username = models.CharField(_('username'),
                                max_length=150,
                                unique=True,
                                validators=[username_validator],
                                help_text=_('Required. 150 characters or fewer, Letters, digits and @/./+/-/_ only.'))
    user_type = models.PositiveSmallIntegerField(null=False,choices=USER_TYPE)
    email = models.EmailField(unique=True, error_messages={'unique':_("A user with that email name already exists.")})
    phone = models.IntegerField(unique=True,null=True)
    address = models.CharField(null=True,max_length=300)
    profile_photo = models.ImageField(upload_to='profile_photo',blank=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''Send an email to this user'''
        send_mail(subject, message, from_email, [self.email], **kwargs)

