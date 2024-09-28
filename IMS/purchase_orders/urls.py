from django.urls import path
from purchase_orders import views

urlpatterns = [
    path('',views.view_purchases,name='purchases'),
    # path('<int:id>/',views.get_purchase,name='purchase'),
    path('make/<int:id>',views.make_purchase,name='make_purchase'),
    path('make/<int:id>/',views.make_purchase,name='make_purchase'),
    path('<int:id>/draft/',views.draft_purchase,name='add_purchase'),
    path('<int:id>/save/',views.purchase,name='purchase'),
    path('purchase_approve/<int:id>/',views.purchase_approve,name='purchase_approve'),
    path('supplier_approve/<int:id>',views.supplier_approve,name='supplier_approve'),
    path('cancel/<int:id>',views.cancel_purchase,name='cancel_purchase'),
    path('supplier/',views.supplier_api,name='supplier_api'),
    path('purchase/',views.purchase_api,name='purchase_api'),
    path('approve/<int:id>/',views.approve,name='p_approve'),
]
 