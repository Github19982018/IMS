from django.urls import include,path
from accounts.views import RegistrationView, logins,profile

urlpatterns = [
               path('login/',logins,name='login'),
               path('profile/',profile,name='profile'),
               path('registration/',RegistrationView.as_view(),name='registration'),
               path('',include('django.contrib.auth.urls')),
               ]