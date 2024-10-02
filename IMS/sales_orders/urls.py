from django.urls import path
from IMS.sales_orders.views import sales,packages,ships

urlpatterns = [
    path('',sales.view_sales,name='sales'),
    path('packages/',packages.view_packages,name='packages'),
    path('ships/',ships.view_ships,name='ships'),
    
    path('<int:id>/',sales.get_sales,name='get_sale'),
    path('packages/<int:id>/',packages.get_package,name='get_package'),
    path('ships/<int:id>/',ships.get_ship,name='get_ship'),
    
    path('draft/',sales.draft_sales,name='make_sales'),
    # path('create/',views.make_sales,name='create_sales'),
    # path('<int:id>/draft/',views.draft_sales,name='draft_sales'),
    path('save/',sales.save_items,name='save_sales'),
    path('<int:id>/save/',sales.sales,name='sale'),
    path('<int:id>/edit/',sales.edit_sales,name='edit_sale'),
    
    path('<int:id>/package_draft/',packages.package_draft,name='package_draft'),
    path('<int:id>/package/',packages.package,name='package'),
    path('package/<int:id>/delete',packages.delete_package,name='delete_package'),
    path('<int:id>/ship/',ships.ship,name='ship'),
    path('<int:id>/ship/create',ships.create_ship,name='create_ship'),
    path('<int:id>/ship/cancel',sales.cancel_ship,name='cancel_ship'),
    path('<int:id>/cancel',sales.cancel_sales,name='cancel_sales'),
    
    path('package_api/',packages.package_api,name='package_api'),
    path('sales_api/',sales.sales_api,name='sales_api'),
    path('ships_api/',ships.ship_api,name='ships_api'),
]