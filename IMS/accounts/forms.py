
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from accounts.models import User

class Registrationform(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User

    
        