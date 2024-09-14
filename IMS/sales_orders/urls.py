from django.urls import path
from sales_orders import views

urlpatterns = [
    path('',views.view_sales,name='sales'),
    path('<int:id>/',views.get_sales,name='get_sale'),
    # path('<int:id>/packages',views.get_sales,name='get_sale'),
    # path('<int:id>/ship',views.get_sales,name='get_shipment'),
    path('get_package/<int:id>/',views.get_package,name='get_package'),
    path('make/',views.make_sales,name='make_sales'),
    path('create/',views.make_sales,name='create_sales'),
    path('<int:id>/draft/',views.draft_sales,name='draft_sales'),
    path('<int:id>/save/',views.sales,name='sale'),
    path('<int:id>/package_draft/',views.package_draft,name='package_draft'),
    path('<int:id>/package/',views.package,name='package'),
    path('<int:id>/ship/',views.ship,name='ship'),
    path('supplier/',views.sales_api,name='supplier_approve'),
]