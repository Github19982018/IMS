from django.urls import path
from reports import views

urlpatterns = [
    path('',views.reports,name='reports'),
    path('purchases/',views.purchase,name='report_purchase'),
    path('sales/',views.sales,name='report_sales'),
    path('inventory/',views.inventory,name='report_inventory')
]