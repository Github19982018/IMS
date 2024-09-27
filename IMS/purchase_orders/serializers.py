
from rest_framework import serializers
from purchase_orders.models import PurchaseItems,PurchaseOrder,Purchase_status,PurchaseDraft



class PurchaseDraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseDraft
        fields = '__all__'

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItems
        fields = ['id','price','quantity','units','item__sku','item__description','item__brand','item__dimensions','item__weight']
        
class PurchaseSrializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'
        depth=2

class PurchasesSerializer(serializers.Serializer):
    ref = serializers.IntegerField()
    items = ItemsSerializer(many=True)
    purchase = PurchaseSrializer()


