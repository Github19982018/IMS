from django.shortcuts import render,redirect
from purchase_orders.models import Purchase,Purchase_status,Purchase_items
from inventory.models import Inventory,Ship_method,Warehouse
from supplier.models import Supplier
from datetime import datetime, date


# Create your views here.
def view_purchases(request):
    purchases = Purchase.objects.all()
    return render(request,template_name='purchases.html',context={'purchases':purchases})
def get_purchase(request,id):
    purchases = Purchase.objects.all()
    return render(request,template_name='purchase_next.html',context={'purchases':purchases})

def make_purchase(request):
    item_id =  request.GET.get('item')
    item = Inventory.objects.get(id=item_id)
    draft = Purchase_items.objects.create(item_id=item,price=item.selling_price,quantity=1,units=item.units)
    return redirect(add_purchase,id=draft.id,permanent=True)

def add_purchase(request,id):
    draft = Purchase_items.objects.get(id=id)
    item = Inventory.objects.get(id=draft.item_id.id)
    suppliers = Supplier.objects.all()
    ship_method = Ship_method.objects.all()
    if request.method == 'POST':
        s = request.GET.get('supplier',item.preferred_supplier)
        if s:
            supplier = Supplier.objects.get(id=s)
        else:
            supplier = suppliers.first()
        bill = request.POST['bill_address']
        ship = request.POST['ship_address']
        sh= request.POST['ship_method']
        ship_method = Ship_method.objects.get(id=sh)
        p_date = request.POST['preferred_date']
        status = Purchase_status.objects.get(status='draft')
        purchase = Purchase(id=draft,warehouse=Warehouse.objects.get(id=1),supplier=supplier,bill_address=bill,preferred_shipping_date=p_date,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status)
        return render(request,template_name='purchase_next.html',context={'number':id,'items':[draft], 'purchase':purchase})
    else:
        s = request.GET.get('supplier',item.preferred_supplier)
        if s:
            supplier = Supplier.objects.get(id=s)
        else:
            supplier = suppliers.first()
        return render(request,template_name='purchase.html',context={'number':id,'item':item,'suppliers':suppliers,'ship_method':ship_method,'supplier':supplier,'date':date.today()})
    
    # def purchase_status(request,id):
        