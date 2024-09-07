from django.urls import path
from .views import view_inventory,get_inventory,add_inventory

urlpatterns = [
    path('',view_inventory,name='inventories'),
    path('<int:id>/',get_inventory,name='inventory'),
    path('add/',add_inventory,name='addinventory'),
]
