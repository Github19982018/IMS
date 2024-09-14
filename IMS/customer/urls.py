from django.urls import path
from customer.views import view_customers,get_customer

urlpatterns = [
    path('',view_customers,name='customers'),
    path('<int:id>',get_customer,name='customer'),
]
