
from rest_framework import serializers
from purchase_orders.models import PurchaseItems,PurchaseOrder,PurchaseStatus,PurchaseDraft
from inventory.models import Inventory



class PurchaseDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDraft
        fields = '__all__'
        
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['sku','name','description','brand','dimensions','weight']

class ItemsSerializer(serializers.ModelSerializer):
    item = InventorySerializer()
    class Meta:
        model = PurchaseItems
        fields = ['id','price','quantity','units','item']
        
class PurchaseSrializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        depth=2

class PurchasesSerializer(serializers.Serializer):
    ref = serializers.IntegerField()
    items = ItemsSerializer(many=True)
    purchase = PurchaseSrializer()


