from django.test import TestCase
from purchase_orders.models import Purchase_status,PurchaseDraft,PurchaseItems,PurchaseOrder

# Create your tests here.
class PurchaseTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.draft = PurchaseDraft.objects.create()
        
     