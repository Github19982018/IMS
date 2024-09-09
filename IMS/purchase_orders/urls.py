from django.urls import path
from purchase_orders import views

urlpatterns = [
    path('',views.view_purchases,name='purchases'),
    # path('<int:id>/',views.get_purchase,name='purchase'),
    path('add/',views.make_purchase,name='add_purchase'),
    path('add/<int:id>/',views.draft_purchase,name='add_purchase'),
    path('save/<int:id>/',views.purchase,name='purchase'),
    path('purchase_approve/<int:id>/',views.purchase_approve,name='purchase_approve'),
]
 