
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from accounts.models import User


class Registrationform(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username','user_type','password','email']



class Userform(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name','last_name','email','address','phone']

    def save(self,commit=True):
        user = super(Userform, self).save(commit=False)
        if commit:
            user.save()
        return user


    
        