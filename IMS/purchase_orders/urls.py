from django.urls import path
from purchase_orders import views

urlpatterns = [
    path('',views.view_purchases,name='purchases'),
    # path('<int:id>/',views.get_purchase,name='purchase'),
    path('make/',views.make_purchase,name='make_purchase'),
    path('<int:id>/make/',views.draft_purchase,name='add_purchase'),
    path('<int:id>/save/',views.purchase,name='purchase'),
    path('purchase_approve/<int:id>/',views.purchase_approve,name='purchase_approve'),
    path('supplier/',views.purchase_api,name='supplier_approve'),
]
 