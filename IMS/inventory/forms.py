from django.forms import ModelForm
from inventory.models import Inventory

class InventoryForm(ModelForm):
    class Meta:
        model = Inventory
        exclude = ['updated']