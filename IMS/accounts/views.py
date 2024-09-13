from django.shortcuts import render
from django.contrib.auth import login
from django.views.generic import CreateView

from accounts.forms import Registrationform
from accounts.models import User

class RegistrationView(CreateView):
    model = User
    form_class = Registrationform
    template_name = 'registration.html'

    def form_valid(self,form):
        form.save()
        
        
