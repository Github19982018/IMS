from django.urls import path
from sales_orders import views

urlpatterns = [
    path('',views.view_sales,name='sales'),
    path('<int:id>/',views.get_sales,name='get_sale'),
    path('make/',views.make_sales,name='make_sales'),
    path('draft/<int:id>',views.draft_sales,name='draft_sales'),
    path('save/<int:id>/',views.sales,name='sale'),
    path('package/<int:id>/',views.package,name='package'),
    path('supplier/',views.sales_api,name='supplier_approve'),
]