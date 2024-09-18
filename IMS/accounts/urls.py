from django.urls import include,path
from accounts.views import RegistrationView, logins,profile,change_password
from django.contrib.auth import views as auth_views

urlpatterns = [
            #    path('login/',auth_views.LoginView.as_view,name='login'),
               path('login/',logins,name='logins'),
               path('profile/',profile,name='profile'),
               path('change_password/',change_password,name='change_password'),
               path('registration/',RegistrationView.as_view(),name='registration'),
               path('',include('django.contrib.auth.urls')),
               ]