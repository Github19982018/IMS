"""
URL configuration for IMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.test import override_settings,SimpleTestCase
from inventory.views import error_response_handler
from dashboard.views import dashboard
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ims/v1/',include('dashboard.urls')),
    path('ims/v1/inventory/',include('inventory.urls')),
    path('ims/v1/purchases/',include('purchase_orders.urls')),
    path('ims/v1/suppliers/',include('supplier.urls')),
    path('ims/v1/customers/',include('customer.urls')),
    path('ims/v1/sales/',include('sales_orders.urls')),
    path('ims/v1/reports/',include('reports.urls')),
    path('ims/v1/accounts/',include('accounts.urls')),
    path('ims/v1/warehouses/',include('warehouse.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = error_response_handler

# @override_settings(ROOT_URLCONF=__name__)
# class CustomErrorHandlerTests(SimpleTestCase):
#     def test_handler_renders_template_response(self):
#         response = self.client.ger('/404/')
#         self.assertContains(response,'Error handler content',status_code=404)