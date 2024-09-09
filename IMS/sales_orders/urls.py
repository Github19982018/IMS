from django.urls import path
from sales_orders import views

urlpatterns = [
    path('',views.view_sales,name='sales'),
    path('<int:id>/',views.get_sales,name='get_sale'),
    path('make/',views.make_sales,name='make_sales'),
    path('draft/<int:id>',views.draft_sales,name='draft_sales'),
    path('save/<int:id>/',views.sales,name='sale'),
    # path('sales_approve/<int:id>/',views.approve_sales,name='approve_sales'),
    path('supplier/',views.sales_api,name='supplier_approve'),
]