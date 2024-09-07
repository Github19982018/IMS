from django.shortcuts import render
from purchase_orders.models import Purchase,Purchase_status
from inventory.models import Inventory
from supplier.models import Supplier


# Create your views here.
def view_purchases(request):
    purchases = Purchase.objects.all()
    return render(request,template_name='purchases.html',context={'purchases':purchases})

def add_purchase(request,id):
    item = Inventory.objects.get(id=id)
    supplier = Supplier.objects.filter()
    if request.method == 'POST':
        return render(request,template_name='purchase_next.html',context={'item':item})
    else:
        return render(request,template_name='purchase.html',context={'item':item,'supplier':supplier})