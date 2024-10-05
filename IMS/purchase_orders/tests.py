from accounts.models import User
from django.test import TestCase
from core.middleware.custom_middleware import Warehouse_middleware
from purchase_orders.models import PurchaseDraft,PurchaseReceive,ReceiveStatus,PurchaseItems,PurchaseOrder,Supplier,ShipMethod,PurchaseStatus
from django.test import Client,RequestFactory
from inventory.models import Warehouse,Inventory
from django.urls import reverse
import datetime
from purchase_orders import views

# Create your tests here.
class PurchaseTests(TestCase):
    @classmethod
    def setUpTestData(self) -> None:
        self.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        self.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        self.item = Inventory.objects.create(name='test',weight=43,sku='sku',purchasing_price=12,selling_price=34,on_hand=55)
        self.supplier = Supplier.objects.create(id=1,phone=2414,name='supplier1',since=datetime.date.today()+datetime.timedelta(days=-10))
        self.draft = PurchaseDraft.objects.create(supplier=self.supplier)
        self.warehouse = Warehouse.objects.create(name='warehouse1')
        self.shipmethod = ShipMethod.objects.create(id=1,method='method1')
        self.purchase_status = PurchaseStatus.objects.create(id=1,status='draft')
        PurchaseStatus.objects.create(id=2,status='test2')
        PurchaseStatus.objects.create(id=3,status='test3')
        PurchaseStatus.objects.create(id=4,status='test3')
        PurchaseStatus.objects.create(id=5,status='test3')
        PurchaseStatus.objects.create(id=6,status='test3')
        PurchaseStatus.objects.create(id=7,status='test3')
        ReceiveStatus.objects.create(id=1,status='test1')
        ReceiveStatus.objects.create(id=2,status='test2')
        ReceiveStatus.objects.create(id=3,status='test3')
        # self.specialist = User.objects.create_user(username='test',password='test',user_type=3)
        
    def setUp(self):
        self.client.force_login(self.specialist)
        self.factory = RequestFactory()
        

    def test_view_purchases(self):
        res  = self.client.get(reverse('purchases'))
        self.assertEqual(res.status_code,200)
    
        
    def test_view_recieved(self):    
        res = self.client.get('/ims/v1/purchases/recieved/')
        self.assertEqual(res.status_code,200)
        
    
    def test_make_purchase_get(self):
        req = self.factory.get('ims/v1/inventories/')
        req.user = self.manager
        res = views.make_purchase(req,id=self.item.id)
        self.assertEqual(res.status_code,302)
        
    def test_make_purchase_post(self):
        req = self.factory.post('ims/v1/inventories/')
        req.user = self.specialist
        res = views.make_purchase(req,id=self.item.id)
        self.assertEqual(res.status_code,302)
        
    def test_make_purchase_fake_id(self):
        req = self.factory.get('ims/v1/inventories/')
        req.user = self.specialist
        res = views.make_purchase(req,id=433)
        self.assertEqual(res.status_code,404)
        
        
    def test_draft_purchase_post(self):
        req = self.factory.post(f'ims/v1/purchases/{self.item.id}/draft')
        req.user = self.specialist
        res = views.draft_purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,302)
        
    def test_draft_purchase_get_no_items(self):
        req = self.factory.get(f'ims/v1/purchases/{self.item.id}/draft')
        req.user = self.specialist
        res = views.draft_purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,404)
        
    def test_draft_purchase_get_with_items(self):
        req = self.factory.get(f'ims/v1/purchases/{self.item.id}/draft')
        req.user = self.specialist
        PurchaseItems.objects.create(purchase=self.draft, item=self.item, price=self.item.selling_price,quantity=3,units='pcs')
        res = views.draft_purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,200)
        
    def test_make_purchase_flow(self):
        res = self.client.get(f'/ims/v1/purchases/make/{self.item.id}/',follow=True)
        self.assertEqual(res.status_code,200)
        
    def test_purchase_fake_id(self):
        res = self.client.get(reverse('purchase',args=[5]))
        self.assertEqual(res.status_code,404)
        
    def test_purchase_post_fakeid(self):
        res = self.client.get(reverse('purchase',args=[5]))
        self.assertEqual(res.status_code,404)
        
    def test_purchase_get_with_no_order(self):
        res = self.client.get(reverse('purchase',args=[self.draft.id]))
        self.assertEqual(res.status_code,404)
        
    def test_purchase_post_with_no_keys(self):
        res = self.client.post(reverse('purchase',args=[self.draft.id]))
        self.assertEqual(res.status_code,400)
        
    def test_purchase_post_with_no_order(self):
        req = self.factory.post(reverse('purchase',args=[self.draft.id]),data={'bill_address':'ab cd','ship_address':'ef gh','ship_method':self.shipmethod.id,'preferred_date':'4/2/2023, 2:34:34 PM'})
        req.w = self.warehouse.id
        res = views.purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,201)
        
    def test_purchase_get_with_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        req = self.factory.get(reverse('add_purchase',args=[self.draft.id]))
        req.w = self.warehouse.id
        res = views.purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,200)
        
    def test_purchase_post_with_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        req = self.factory.post(reverse('purchase',args=[self.draft.id]),data={'bill_address':'ab cd','ship_address':'ef gh','ship_method':self.shipmethod.id,'preferred_date':'4/2/2023, 2:34:34 PM'})
        req.user = self.specialist
        req.w = self.warehouse.id
        res = views.purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,201)
        
    def test_purchase_post_with_cancelled_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,cancel=True,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        req = self.factory.post(reverse('purchase',args=[self.draft.id]),data={'bill_address':'ab cd','ship_address':'ef gh','ship_method':self.shipmethod.id,'preferred_date':'4/2/2023, 2:34:34 PM'})
        req.user = self.specialist
        req.w = self.warehouse.id
        res = views.purchase(req,id=self.draft.id)
        self.assertEqual(res.status_code,400)
        
    def test_cancel_purchase_fake_id(self):
        res = self.client.get(reverse('cancel_purchase',args=[7867]))
        self.assertEqual(res.status_code,404)
        
    def test_cancel_purchase_no_order(self):
        res = self.client.get(reverse('cancel_purchase',args=[self.draft.id]))
        self.assertEqual(res.status_code,404)
        
    def test_cancel_purchase_with_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('cancel_purchase',args=[self.draft.id]))
        self.assertEqual(res.status_code,302)
        
    def test_cancel_purchase_id_2(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=2),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('cancel_purchase',args=[self.draft.id]))
        self.assertEqual(res.status_code,302)
        
    def test_purchase_approve_fake_id(self):
        res = self.client.get(reverse('purchase_approve',args=[7867]))
        self.assertEqual(res.status_code,404)
        
    def test_purchase_approve_no_order(self):
        res = self.client.get(reverse('purchase_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,404)
        
    def test_purchase_approve_with_status_draft_and_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('purchase_approve',args=[self.draft.id]))
        # self.assertEqual(res.status_code,302) #no onnection
        self.assertEqual(res.status_code,201) #with onnection
        
    def test_purchase_approve_status_not_draft(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=2),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('purchase_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,201)
        
    def test_purchase_approve_cancelled(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,cancel=True,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('purchase_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,302)    
        
    def test_supplier_approve_fake_id(self):
        res = self.client.get(reverse('supplier_approve',args=[7867]))
        self.assertEqual(res.status_code,404)
        
    def test_supplier_approve_no_order(self):
        res = self.client.get(reverse('supplier_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,404)
        
    def test_supplier_approve_with_status_draft_and_order(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('supplier_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,401)
        
    def test_supplier_approve_status_purchase_approved(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=2),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.get(reverse('supplier_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,200)
        
    def test_supplier_approve_cancelled(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,cancel=True,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('supplier_approve',args=[self.draft.id]))
        self.assertEqual(res.status_code,401)    
    
    def test_recieve_api_invalid_request(self):
        res = self.client.post(reverse('recieve_api'),data={'a':'g'})
        self.assertEqual(res.status_code,400)
        
    def test_recieve_api_fake_ref(self):
        res = self.client.post(reverse('recieve_api'),data={'ref':453,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_recieve_api_no_order(self):
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_recieve_api_not_dispatched(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,401)
        
    def test_recieve_api_cancelled(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,cancel=True,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,401)
        
    def test_recieve_api_dispatched_status_1(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':1})
        self.assertEqual(res.status_code,201)
        
    def test_recieve_api_dispatched_status_2(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        self.recieve = PurchaseReceive.objects.create(ref=self.draft,status=ReceiveStatus(1))
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,201)
        
    def test_recieve_api_dispatched_status_3(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        self.recieve = PurchaseReceive.objects.create(ref=self.draft,status=ReceiveStatus(1))
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':3})
        self.assertEqual(res.status_code,201)
        
    def test_recieve_api_fake_status(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('recieve_api'),data={'ref':self.draft.id,'status':19})
        self.assertEqual(res.status_code,400)
        
    def test_supplier_api_invalid_request(self):
        res = self.client.post(reverse('supplier_api'),data={'a':'g'})
        self.assertEqual(res.status_code,400)
        
    def test_supplier_api_fake_ref(self):
        res = self.client.post(reverse('supplier_api'),data={'ref':453,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_supplier_api_no_order(self):
        res = self.client.post(reverse('supplier_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_supplier_api_not_dispatched(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('supplier_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,201)
        
    def test_supplier_api_dispatched(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('supplier_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,201)
        
    def test_supplier_api_cancelled(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,cancel=True,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('supplier_api'),data={'ref':self.draft.id,'status':2})
        self.assertEqual(res.status_code,401)
        
    def test_supplier_api_fake_status(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,cancel=True,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('supplier_api'),data={'ref':self.draft.id,'status':19})
        self.assertEqual(res.status_code,400)
        
    
    def test_purchase_api_invalid_request(self):
        res = self.client.post(reverse('purchase_api'),data={'a':'g'})
        self.assertEqual(res.status_code,400)
        
    def test_purchase_api_fake_ref(self):
        res = self.client.post(reverse('purchase_api'),data={'ref':453,'status':2})
        self.assertEqual(res.status_code,404)
        
    def test_purchase_api_no_order(self):
        res = self.client.post(reverse('purchase_api'),data={'ref':self.draft.id})
        self.assertEqual(res.status_code,404)
        
    def test_purchase_api_status_draft(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=self.purchase_status,warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('purchase_api'),data={'ref':self.draft.id})
        self.assertEqual(res.status_code,201)
        
    def test_purchase_api_status_not_draft(self):
        self.order = PurchaseOrder.objects.create(id=self.draft,total_amount=2343,created_date=datetime.datetime.now(),ship_method=ShipMethod.objects.first(),status=PurchaseStatus.objects.get(id=6),warehouse=self.warehouse,contact_phone=3242)
        res = self.client.post(reverse('purchase_api'),data={'ref':self.draft.id})
        self.assertEqual(res.status_code,400)
        
        
    