from django.urls import path
from inventory import views

urlpatterns = [
    path('',views.view_inventory,name='inventories'),
    path('<int:id>/',views.inventory,name='inventory'),
    path('add/',views.add_inventory,name='addinventory'),
    path('<int:id>/update/',views.update_inventory,name='updateinventory'),
]
