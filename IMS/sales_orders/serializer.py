from rest_framework import serializers
from sales_orders.models import Sales, SalesItems,Shipment,Package

from django.db.models import fields

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItems
        fields = '__all__'
        
class SalesSerializer(serializers.ModelSerializer):
    items = ItemsSerializer(many=True)
    class Meta:
        model = Sales
        fields = '__all__'

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItems
        fields = '__all__'
        
class ShipSerializer(serializers.ModelSerializer):
    # items = ItemsSerializer(many=True)
    class Meta:
        model = Shipment
        # fields = '__all__'
        exclude = ['shipment_date','sales','customer','status']
        # depth = 3

class PackageSerializer(serializers.ModelSerializer):
    # items=ItemsSerializer(many=True)

    class Meta:
        model = Package
        fields = '__all__'
        depth = 3
