from django.urls import path
from warehouse import views

urlpatterns = [
    path('',views.view_warehouse,name='warehouses'),
    path('<int:id>/',views.get_warehouse,name='warehouse'),
    path('add/',views.add_warehouse,name='addwarehouse'),
    path('<int:id>/update/',views.update_warehouse,name='updatewarehouse'),
]
