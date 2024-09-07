from django.urls import path
from purchase_orders import views

urlpatterns = [
    path('',views.view_purchases,name='purchases'),
    # path('<int:id>/',views.get_purchase,name='purchase'),
    path('add/',views.add_purchase,name='add_purchase'),
]
 