from accounts.models import User
from django.test import TestCase
from core.middleware.custom_middleware import Warehouse_middleware
from purchase_orders.models import PurchaseDraft,PurchaseItems,PurchaseOrder
from django.test import Client
from inventory.models import Warehouse
from django.urls import reverse

# Create your tests here.
class PurchaseTests(TestCase):
    def setUp(self) -> None:
        self.specialist = User.objects.create_user(username='test',password='test',email='23525',user_type=3)
        self.manager = User.objects.create_user(username='manager',password='manager',email='45325',user_type=2)
        # self.specialist = User.objects.create_user(username='test',password='test',user_type=3)
        self.client.force_login(self.specialist)

    def test_view_purchases(self):
        res  = self.client.get(reverse('purchases'))
        self.assertEqual(res.status_code,200)
    
        
    def test_view_recieved(self):    
        res = self.client.get('/ims/v1/purchases/recieved/')
        self.assertEqual(res.status_code,200)
    
        
     