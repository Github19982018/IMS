from django.urls import path
from supplier.views import view_suppliers,supplier,supplier_orders

urlpatterns = [
    path('',view_suppliers,name='suppliers'),
    path('<int:id>/',supplier,name='supplier'),
    path('<int:id>/orders/',supplier_orders,name='supplierOrders'),
]
