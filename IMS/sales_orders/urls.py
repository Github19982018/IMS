from django.urls import path
from sales_orders.views import sales,packages,ships

urlpatterns = [
    path('',sales.view_sales,name='sales'),
    path('<int:id>/',sales.get_sales,name='get_sale'),
    path('draft/',sales.draft_sales,name='make_sales'),
    path('save/',sales.save_items,name='save_sales'),
    path('<int:id>/save/',sales.sales,name='sale'),
    path('<int:id>/edit/',sales.edit_sales,name='edit_sale'),
    path('<int:mid>/cancel/',sales.cancel_sales,name='cancel_sales'),
    path('sales_api/',sales.sales_api,name='sales_api'),
    
    path('packages/',packages.view_packages,name='packages'),
    path('packages/<int:id>/',packages.get_package,name='get_package'),
    path('<int:id>/package_draft/',packages.package_draft,name='package_draft'),
    path('<int:id>/package/',packages.package,name='package'),
    path('packages/<int:id>/delete/',packages.delete_package,name='delete_package'),
    path('package_api/',packages.package_api,name='package_api'),
    
    # path('create/',views.make_sales,name='create_sales'),
    # path('<int:id>/draft/',views.draft_sales,name='draft_sales'),
    
    path('ships/',ships.view_ships,name='ships'),
    path('ships/<int:id>/',ships.get_ship,name='get_ship'),
    path('<int:id>/ship/',ships.ship,name='ship'),
    path('<int:id>/ship/create/',ships.create_ship,name='create_ship'),
    path('<int:id>/ship/cancel/',ships.cancel_ship,name='cancel_ship'),
    path('ships_api/',ships.ship_api,name='ships_api'),
    
]