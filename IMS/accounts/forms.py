
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm,UserChangeForm
from django.db import transaction
from accounts.models import User


class Registrationform(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username','user_type','password','email']



class Updateform(forms.ModelForm):
    username = forms.CharField(max_length=150,required=True)
    first_name = forms.CharField(max_length=150,required=True)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True,)
    address = forms.CharField(max_length=400)
    phone = forms.IntegerField()
    profie_photo = forms.ImageField(required=False)
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','address','phone','profile_photo']


    
        