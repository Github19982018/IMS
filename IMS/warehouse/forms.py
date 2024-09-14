from django.forms import ModelForm
from warehouse.models import Warehouse

class WarehouseForm(ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'
