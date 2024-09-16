
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction

from accounts.models import User,Manager,Specialist

class Registrationform(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username','user_type','is_active','password','email']

class UserAuthenticationForm(AuthenticationForm):
    user_type = forms.ChoiceField()
    # email = forms.EmailField(required=True)
    # class Meta(AuthenticationForm.Meta):
    #     model = User
    #     fields = ['username','user_type','password','email']

    
        