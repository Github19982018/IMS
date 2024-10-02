from django.test import TestCase
from accounts.models import User
from core.middleware.custom_middleware import Warehouse_middleware
from sales_orders.models import Customer,Sales,SalesItems,SalesStatus,Shipment,ShipMethod,ShipStatus,PackageStatus,Package,PackageItems
from django.test import Client,RequestFactory
from inventory.models import Warehouse,Inventory
from django.urls import reverse
import datetime
from sales_orders.views import sales,ships,packages

# Create your tests here.
class SalesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku',purchasing_price=12,selling_price=34,on_hand=55)
        cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku',purchasing_price=122,selling_price=324,on_hand=5)
        cls.customer = Customer.objects.create(id=1,phone=2414,name='supplier1',since=datetime.date.today()+datetime.timedelta(days=-10))
        cls.warehouse = Warehouse.objects.create(name='warehouse1')
        cls.shipmethod = ShipMethod.objects.create(id=1,method='method1')
        SalesStatus.objects.create(id=1,status='test1')
        SalesStatus.objects.create(id=2,status='test2')
        SalesStatus.objects.create(id=3,status='test3')
        SalesStatus.objects.create(id=4,status='test3')
        SalesStatus.objects.create(id=5,status='test3')
        SalesStatus.objects.create(id=6,status='test3')
        SalesStatus.objects.create(id=7,status='test3')
        PackageStatus.objects.create(id=1,status='test1')
        PackageStatus.objects.create(id=2,status='test2')
        PackageStatus.objects.create(id=3,status='test3')
        PackageStatus.objects.create(id=4,status='test4')
        ShipStatus.objects.create(id=1,status='test1')
        ShipStatus.objects.create(id=2,status='test2')
        ShipStatus.objects.create(id=3,status='test3')
        ShipStatus.objects.create(id=4,status='test4')
  
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        
class PacakageTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku',purchasing_price=12,selling_price=34,on_hand=55)
        cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku',purchasing_price=122,selling_price=324,on_hand=5)
        cls.customer = Customer.objects.create(id=1,phone=2414,name='supplier1',since=datetime.date.today()+datetime.timedelta(days=-10))
        cls.warehouse = Warehouse.objects.create(name='warehouse1')
        cls.shipmethod = ShipMethod.objects.create(id=1,method='method1')
        SalesStatus.objects.create(id=1,status='test1')
        SalesStatus.objects.create(id=2,status='test2')
        SalesStatus.objects.create(id=3,status='test3')
        SalesStatus.objects.create(id=4,status='test3')
        SalesStatus.objects.create(id=5,status='test3')
        SalesStatus.objects.create(id=6,status='test3')
        SalesStatus.objects.create(id=7,status='test3')
        PackageStatus.objects.create(id=1,status='test1')
        PackageStatus.objects.create(id=2,status='test2')
        PackageStatus.objects.create(id=3,status='test3')
        PackageStatus.objects.create(id=4,status='test4')
        ShipStatus.objects.create(id=1,status='test1')
        ShipStatus.objects.create(id=2,status='test2')
        ShipStatus.objects.create(id=3,status='test3')
        ShipStatus.objects.create(id=4,status='test4')
  
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        
    def test_view_sales(self):
        res  = self.client.get(reverse('sales'))
        self.assertEqual(res.status_code,200)
        
class ShipmentTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku',purchasing_price=12,selling_price=34,on_hand=55)
        cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku',purchasing_price=122,selling_price=324,on_hand=5)
        cls.customer = Customer.objects.create(id=1,phone=2414,name='supplier1',since=datetime.date.today()+datetime.timedelta(days=-10))
        cls.warehouse = Warehouse.objects.create(name='warehouse1')
        cls.shipmethod = ShipMethod.objects.create(id=1,method='method1')
        SalesStatus.objects.create(id=1,status='test1')
        SalesStatus.objects.create(id=2,status='test2')
        SalesStatus.objects.create(id=3,status='test3')
        SalesStatus.objects.create(id=4,status='test3')
        SalesStatus.objects.create(id=5,status='test3')
        SalesStatus.objects.create(id=6,status='test3')
        SalesStatus.objects.create(id=7,status='test3')
        PackageStatus.objects.create(id=1,status='test1')
        PackageStatus.objects.create(id=2,status='test2')
        PackageStatus.objects.create(id=3,status='test3')
        PackageStatus.objects.create(id=4,status='test4')
        ShipStatus.objects.create(id=1,status='test1')
        ShipStatus.objects.create(id=2,status='test2')
        ShipStatus.objects.create(id=3,status='test3')
        ShipStatus.objects.create(id=4,status='test4')
  
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        
    