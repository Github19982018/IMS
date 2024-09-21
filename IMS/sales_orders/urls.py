from django.urls import path
from sales_orders import views

urlpatterns = [
    path('',views.view_sales,name='sales'),
    path('packages/',views.view_packages,name='packages'),
    path('ships/',views.view_ships,name='ships'),
    
    path('<int:id>/',views.get_sales,name='get_sale'),
    path('packages/<int:id>/',views.get_package,name='get_package'),
    path('ships/<int:id>/',views.get_ship,name='get_ship'),
    
    path('draft/',views.draft_sales,name='make_sales'),
    # path('create/',views.make_sales,name='create_sales'),
    # path('<int:id>/draft/',views.draft_sales,name='draft_sales'),
    path('save/',views.save_quantity,name='save_sales'),
    path('<int:id>/save/',views.sales,name='sale'),
    path('<int:id>/edit/',views.edit_sales,name='edit_sale'),
    
    path('<int:id>/package_draft/',views.package_draft,name='package_draft'),
    path('<int:id>/package/',views.package,name='package'),
    path('/package/<int:id>/delete',views.delete_package,name='delete_package'),
    path('<int:id>/ship/',views.ship,name='ship'),
    path('<int:id>/ship/create',views.create_ship,name='create_ship'),
    
    path('supplier_api/',views.sales_approve,name='supplier_approve'),
    path('package_api/',views.package_api,name='package_api'),
    path('sales_api/',views.sales_api,name='sales_api'),
]