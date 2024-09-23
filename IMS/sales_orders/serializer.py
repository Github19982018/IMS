from rest_framework import serializers
from sales_orders.models import Sales, SalesItems,Shipment,Package

from django.db.models import fields

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItems
        fields = '__all__'
        
class SaleSerializer(serializers.ModelSerializer):
    items = ItemsSerializer(many=True)
    class Meta:
        model = Sales
        fields = '__all__'
        depth=2


        
class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = '__all__'
        # exclude = ['shipment_date','sales','customer','status']

class SalesSerializer(serializers.Serializer):
    ref = serializers.IntegerField(required=True)
    items = ItemsSerializer(many=True)
    sales = SaleSerializer

class PackSerializer(serializers.Serializer):
    ref = serializers.IntegerField(required=True)
    items = ItemsSerializer(many=True)
    package = PackageSerializer()


class ShipSerializer(serializers.Serializer):
    ref=serializers.IntegerField(required=True)
    shipment = ShipmentSerializer()
    items = ItemsSerializer(many=True)
    packages = PackageSerializer(many=True)


class ApiSerializer(serializers.Serializer):
    ref = serializers.IntegerField()
    status = serializers.IntegerField(min_value=0, max_value=10)


