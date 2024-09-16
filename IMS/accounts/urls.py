from django.urls import include,path
from accounts.views import RegistrationView, logins

urlpatterns = [
               path('login/',logins,name='login'),
               path('registration/',RegistrationView.as_view(),name='registration'),
               path('',include('django.contrib.auth.urls')),
               ]