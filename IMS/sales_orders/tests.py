from django.test import TestCase
from accounts.models import User
from core.middleware.custom_middleware import Warehouse_middleware
from sales_orders.models import Customer,Sales,SalesItems,SalesStatus,Shipment,ShipMethod,ShipStatus,PackageStatus,Package,PackageItems
from django.test import Client,RequestFactory
from inventory.models import Warehouse,Inventory
from django.urls import reverse
import datetime
from django.contrib import messages
from sales_orders.views import sales,ships,packages

# Create your tests here.
class SalesTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku1',purchasing_price=12,selling_price=34,on_hand=55)
        cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku2',purchasing_price=122,selling_price=324,on_hand=5)
        cls.customer = Customer.objects.create(id=1,phone=2414,name='customer')
        cls.warehouse = Warehouse.objects.create(name='warehouse1')
        cls.shipmethod = ShipMethod.objects.create(id=1,method='method1')
        SalesStatus.objects.create(id=1,status='draft')
        SalesStatus.objects.create(id=2,status='test2')
        SalesStatus.objects.create(id=3,status='test3')
        SalesStatus.objects.create(id=4,status='test3')
        SalesStatus.objects.create(id=5,status='test3')
        SalesStatus.objects.create(id=6,status='test3')
        SalesStatus.objects.create(id=7,status='test3')
        # PackageStatus.objects.create(id=1,status='test1')
        # PackageStatus.objects.create(id=2,status='test2')
        # PackageStatus.objects.create(id=3,status='test3')
        # PackageStatus.objects.create(id=4,status='test4')
        # ShipStatus.objects.create(id=1,status='test1')
        # ShipStatus.objects.create(id=2,status='test2')
        # ShipStatus.objects.create(id=3,status='test3')
        # ShipStatus.objects.create(id=4,status='test4')
  
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        
    def test_view_sales(self):
        res  = self.client.get(reverse('sales'))
        self.assertEqual(res.status_code,200)
        
    def test_get_sales(self):
        self.sales1 = Sales.objects.create(status=SalesStatus.objects.get(id=1),warehouse=Warehouse.objects.first())
        res  = self.client.get(reverse('get_sale',args=[self.sales1.id]))
        self.assertEqual(res.status_code,200)
        
    def test_get_sales_invalid_id(self):
        self.sales1 = Sales.objects.create(status=SalesStatus.objects.get(id=1),warehouse=Warehouse.objects.first())
        res  = self.client.get(reverse('get_sale',args=[324542436]))
        self.assertEqual(res.status_code,404)
        
    def test_draft_sales_manager(self):
        req = self.factory.get('ims/v1/inventories/')
        req.user = self.manager
        res = sales.draft_sales(req)
        self.assertEqual(res.status_code,302)
        
    def test_draft_sales_get(self):
        req = self.factory.get('ims/v1/inventories/')
        req.user = self.specialist
        res = sales.draft_sales(req)
        self.assertEqual(res.status_code,404)
        
    def test_draft_sales_post(self):
        req = self.factory.post('ims/v1/inventories/',{'item':[self.item1.id,self.item2.id]})
        req.user = self.specialist
        res = sales.draft_sales(req)
        self.assertEqual(res.status_code,200)
        self.assertContains(res,text=self.item1.name)
  
    def test_draft_sales_post_no_keys_or_invalid_keys(self):
        res = self.client.post(reverse(sales.draft_sales))
        self.assertEqual(res.status_code,302)
  
    def test_draft_sales_post_invalid_values(self):
        res = self.client.post(reverse(sales.draft_sales),data={'item':[343425]})
        self.assertEqual(res.status_code,302)
        
    def test_save_items_get(self):
        res = self.client.get(reverse(sales.save_items))
        self.assertEqual(res.status_code,404)
        
    def test_save_items_post_no_data(self):
        res = self.client.post(reverse(sales.save_items))
        self.assertEqual(res.status_code,404)
        
    def test_save_items(self):
        res = self.client.post(reverse(sales.save_items),data={'item':[self.item1.id,self.item2.id],'quantity':[10,4]})
        self.assertEqual(res.status_code,302)
  
    def test_save_items_post_invalid_values(self):
        res = self.client.post(reverse(sales.draft_sales),data={'item':[000]})
        self.assertEqual(res.status_code,302)
    
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        self.req = self.factory.get('ims/v1/inventories/')
        self.req.user = self.specialist
        self.sales1 = Sales.objects.create(status=SalesStatus.objects.get(id=2), warehouse=self.warehouse)
        # self.req.w = self.warehouse.id
        
    def test_sales_get(self):
        res = sales.sales(self.req,id=self.sales1.id)
        self.assertEqual(res.status_code,200)
        
    def test_sales_get_invalid_id(self):
        res = sales.sales(self.req,id=34524)
        self.assertEqual(res.status_code,404)
        
    def test_sales(self):
        res = self.client.post(reverse(sales.sales,args=[self.sales1.id]),data={'bill_address':'abcd','ship_address':'efgh','ship_method': self.shipmethod.id,'customer':self.customer.id,'preferred_date':'4/2/2023, 2:34:34 PM'})
        self.assertEqual(res.status_code,200)
  
    def test_sales_post_invalid_values(self):
        res = self.client.post(reverse(sales.sales,args=[self.sales1.id]),data={'bill_address':'abcd','ship_address':'efgh','ship_method': self.shipmethod.id,'customer':4,'preferred_date':'4/2/2023, 2:34:34 PM'})
        self.assertEqual(res.status_code,302)
        
 
    
    
  
  
  
  
  
  
        
class PackageTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku1',purchasing_price=12,selling_price=34,on_hand=55)
        cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku2',purchasing_price=122,selling_price=324,on_hand=5)
        cls.customer = Customer.objects.create(id=1,phone=2414,name='customer')
        cls.warehouse = Warehouse.objects.create(name='warehouse1')
        cls.shipmethod = ShipMethod.objects.create(id=1, method='method1')
        SalesStatus.objects.create(id=1,status='draft')
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
        cls.sales = Sales.objects.create(status=SalesStatus.objects.get(id=1), warehouse=Warehouse.objects.first(),customer=cls.customer)
  
  
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        
    def test_view_packages(self):
        res  = self.client.get(reverse('packages'))
        self.assertEqual(res.status_code,200)
        
    def test_get_package(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.get(reverse(packages.get_package,args=[self.package1.id]))
        self.assertEqual(res.status_code,200)
        
    def test_edit_package_get(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.get(reverse('edit_package',args=[self.package1.id]))
        self.assertEqual(res.status_code,200)
        
    def test_edit_package_post(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('edit_package',args=[self.package1.id]),{'customer':self.customer.id,'ship_address':'sfsf'})
        self.assertEqual(res.status_code,200)
        self.assertContains(res,text='send to sales team')
        # self.assertContains(res,text='Cant connect') #when no connection
        
    def test_edit_package_post_invalid_customer(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('edit_package',args=[self.package1.id]),{'customer':679,'ship_address':'sfsf'})
        self.assertEqual(res.status_code,200)
        self.assertContains(res,text='Invalid customer')
        
    def test_package_draft_get(self):
        res  = self.client.get(reverse('package_draft',args=[self.sales.id]))
        self.assertEqual(res.status_code,200)
        
    def test_package_draft_get_salestatus_not_draft(self):
        self.sale2 = Sales.objects.create(warehouse=self.warehouse,customer=self.customer,status=SalesStatus.objects.get(id=2))
        res  = self.client.get(reverse('package_draft',args=[self.sale2.id]))
        self.assertEqual(res.status_code,400)
        
    def test_package_draft_get_invalid_sales(self):
        res  = self.client.get(reverse('package_draft',args=[3457]))
        self.assertEqual(res.status_code,404)
        
    def test_package_draft_post(self):
        res  = self.client.post(reverse('package_draft',args=[self.sales.id]),{'customer':self.customer.id,'ship_address':'sfhsfh','quantity':[1,3],'item':[self.item1.id,self.item2.id]})
        self.assertEqual(res.status_code,200)
        
    def test_package_draft_post_invalid_customer(self):
        res  = self.client.post(reverse('package_draft',args=[self.sales.id]),{'custom':self.customer.id,'ship_address':'sfhsfh','quantity':[1,3],'item':[self.item1.id,self.item2.id]})
        self.assertEqual(res.status_code,200)
        
    def test_package_draft_post_no_items(self):
        res  = self.client.post(reverse('package_draft',args=[self.sales.id]),{'customer':self.customer.id,'ship_address':'sfhsfh','quantity':[1,3],'item':[]})
        self.assertEqual(res.status_code,404)
        
    def test_package_api_get(self):
        res  = self.client.get(reverse('package_api'))
        self.assertEqual(res.status_code,405)
        
    def test_package_api_post(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('package_api'),{'ref':self.package1.id,'status':2})
        self.assertEqual(res.status_code,201)
        
    def test_package_api_post_invalid_id(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('package_api'),{'ref':4745,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_package_api_post_invalid_status(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('package_api'),{'ref':self.package1.id,'status':98})
        self.assertEqual(res.status_code,400)
        
    def test_package_api_post_cancelled_or_already_updated(self):
        self.package1 = Package.objects.create(sales=self.sales,customer=self.sales.customer,status=PackageStatus.objects.get(id=1))
        res  = self.client.post(reverse('package_api'),{'ref':self.package1.id,'status':4})
        self.assertEqual(res.status_code,400)
        
    # def test_package_api_post_invalid_customer(self):
    #     res  = self.client.post(reverse('package_api',args=[self.sales.id]),{'custom':self.customer.id,'ship_address':'sfhsfh','quantity':[1,3],'item':[self.item1.id,self.item2.id]})
    #     self.assertEqual(res.status_code,200)
        
    # def test_package_api_post_no_items(self):
    #     res  = self.client.post(reverse('package_api',args=[self.sales.id]),{'custom':self.customer.id,'ship_address':'sfhsfh','quantity':[1,3],'item':[]})
    #     self.assertEqual(res.status_code,404)
        
    
   
   
# class ShipmentTests(TestCase):
#     @classmethod
#     def setUpTestData(cls) -> None:
#         cls.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
#         cls.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
#         cls.item1 = Inventory.objects.create(name='test',weight=43,sku='sku1',purchasing_price=12,selling_price=34,on_hand=55)
#         cls.item2 = Inventory.objects.create(name='test2',weight=4,sku='sku2',purchasing_price=122,selling_price=324,on_hand=5)
#         cls.customer = Customer.objects.create(id=1,phone=2414,name='customer',since=datetime.date.today()+datetime.timedelta(days=-10))
#         cls.warehouse = Warehouse.objects.create(name='warehouse1')
#         cls.shipmethod = ShipMethod.objects.create(id=1,method='method1')
#         SalesStatus.objects.create(id=1,status='test1')
#         SalesStatus.objects.create(id=2,status='test2')
#         SalesStatus.objects.create(id=3,status='test3')
#         SalesStatus.objects.create(id=4,status='test3')
#         SalesStatus.objects.create(id=5,status='test3')
#         SalesStatus.objects.create(id=6,status='test3')
#         SalesStatus.objects.create(id=7,status='test3')
#         PackageStatus.objects.create(id=1,status='test1')
#         PackageStatus.objects.create(id=2,status='test2')
#         PackageStatus.objects.create(id=3,status='test3')
#         PackageStatus.objects.create(id=4,status='test4')
#         ShipStatus.objects.create(id=1,status='test1')
#         ShipStatus.objects.create(id=2,status='test2')
#         ShipStatus.objects.create(id=3,status='test3')
#         ShipStatus.objects.create(id=4,status='test4')
  
#     def setUp(self):
#         self.client.force_login(self.specialist)
#         self.factory = RequestFactory()
        
    