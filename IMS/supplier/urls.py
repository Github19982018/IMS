from django.urls import path
from supplier.views import view_suppliers,get_supplier

urlpatterns = [
    path('',view_suppliers,name='suppliers'),
    path('<int:id>',get_supplier,name='supplier'),
]
