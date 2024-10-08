from django.urls import path
from purchase_orders import views

urlpatterns = [
    path('',views.view_purchases,name='purchases'),
    path('recieved/',views.view_recieved,name='recieved'),
    path('<int:id>/',views.get_purchase,name='get_purchase'),
    # path('<int:id>/',views.get_purchase,name='purchase'),
    path('make/<int:id>/',views.make_purchase,name='make_purchase'),
    path('<int:id>/draft/',views.draft_purchase,name='add_purchase'),
    path('<int:id>/save/',views.purchase,name='purchase'),
    path('<int:id>/purchase_approve/',views.purchase_approve,name='purchase_approve'),
    path('<int:id>/supplier_approve/',views.supplier_approve,name='supplier_approve'),
    path('<int:id>/cancel/',views.cancel_purchase,name='cancel_purchase'),
    path('supplier/',views.supplier_api,name='supplier_api'),
    path('purchase/',views.purchase_api,name='purchase_api'),
    path('supplier/recieve/',views.recieve_api,name='recieve_api'),
    path('approve/<int:id>/',views.approve,name='p_approve'),
]
 