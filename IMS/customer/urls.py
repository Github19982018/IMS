from django.urls import path
from customer.views import view_customers,get_customer,customer_orders

urlpatterns = [
    path('',view_customers,name='customers'),
    path('<int:id>',get_customer,name='customer'),
    path('<int:id>/orders/',customer_orders,name='customerOrders'),
]
