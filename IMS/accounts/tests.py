from django.test import TestCase
from django.test import Client
from core.models import User
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from core.middleware.custom_middleware import Warehouse_middleware

class AccountTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test',password='test',user_type=3)
        
    # def test_authenticate(self):
    #     self.client.login(username='test',password='test',user_type=3)
    #     res  = self.client.get(reverse('inventories'))
    #     self.assertEqual(res.status_code,200)
        
    def test_login_no_usertype(self):
        res = self.client.post('/ims/v1/accounts/login/',{'username':'test','password':'test'})
        self.assertEqual(res.status_code,401)
        
    def test_login_usertype(self):
        res = self.client.post('/ims/v1/accounts/login/',{'username':'test','password':'test','user_type':3})
        self.assertEqual(res.status_code,302)


