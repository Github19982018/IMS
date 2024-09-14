from django.template.response import TemplateResponse as render
from django.shortcuts import redirect,HttpResponseRedirect,HttpResponse
from purchase_orders.models import PurchaseOrder,PurchaseReceive,Purchase_status,PurchaseItems,PurchasesItems
from inventory.models import Inventory,ShipMethod
from warehouse.models import Warehouse
from supplier.models import Supplier
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

# Create your views here.
def view_purchases(request):
    purchases = PurchaseOrder.objects.all()
    return render(request,'purchases.html',{'purchases':purchases})
# def get_purchase(request,id):
#     draft = Purchase_items.objects.get(pk=id)
#     purchase = Purchase.objects.get(id=draft)
#     return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})

# making purchase from inventory
def make_purchase(request):
    id_list =  request.GET.getlist('item') 
    items = Inventory.objects.filter(id__in=id_list)
    if len(items)>=1:
        purchase_list = []
        w = request.w
        # warehouse = Warehouse.objects.get(id=w)
        warehouse = Warehouse.objects.all()
        purchase = PurchaseReceive.objects.create(warehouse=warehouse.first())
        for i in items:
            purchase_list.append(PurchasesItems(
                purchase = purchase,
                item_id = i,
                price = i.selling_price,
                quantity = 1,
                units = i.units
            ))
        draft = PurchasesItems.objects.bulk_create(purchase_list)
        return redirect(draft_purchase,id=purchase.id,permanent=True)
    else:
        return render(request,'404.html',{})

def draft_purchase(request,id):
    draft = PurchaseItems.objects.filter(puchase=id)
    suppliers = Supplier.objects.all()
    ship_method = ShipMethod.objects.all()
    supplier = ''
    s = request.GET.get('supplier',draft.item_id.preferred_supplier)
    if s:
        supplier = Supplier.objects.get(id=s)
    else:
        supplier = suppliers.first()
    draft.supplier = supplier
    draft.save()
    return render(request,'purchase.html',{'number':id,'item':draft,'suppliers':suppliers,'ship_method':ship_method,'supplier':supplier,'date':datetime.today()})

def purchase(request,id):
    purchase = PurchaseOrder.objects.get(id=id)
    if purchase:
        draft = PurchaseItems.objects.get(puchase=purchase)
        if purchase.status.id > 1:
            return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})
        else:
            if request.method == 'POST':
                supplier = draft.supplier
                bill = request.POST['bill_address']
                ship = request.POST['ship_address']
                sh= request.POST['ship_method']
                ship_method = ShipMethod.objects.get(id=sh)
                p_date = request.POST['preferred_date']
                status = Purchase_status.objects.get(status='draft')
                purchase = PurchaseOrder.objects.create(id=draft,warehouse=Warehouse.objects.get(id=1),supplier=supplier,bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=draft.total_price)
                return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})
    else:
        return render(request,'404.html',{})

def purchase_approve(request,id):
    draft = PurchaseItems.objects.get(id=id)
    status = Purchase_status(id=4)
    purchase = PurchaseOrder.objects.get(id=draft)
    purchase.status = status
    purchase.save()
    url = 'http://localhost:8081/purchases/approve'
    data = {
        'ref':purchase.id.id,
        'supplier':purchase.supplier.name,
        'contact_person':purchase.supplier.contact_person,
        'bill_address':purchase.bill_address,
        'preferred_shipping_date':purchase.preferred_shipping_date.isoformat(),
        "ship_address":purchase.ship_address,
        'ship_method':purchase.ship_method.method,
        'contact_phone':int(purchase.contact_phone),
        'created_date':purchase.created_date.isoformat(),
        'total_amount':int(purchase.total_amount),
        "items":{'item_id':draft.item_id.id,
                 'price':int(draft.price),
                 'quantity':int(draft.quantity),
                 'units':draft.units}
    }
    requests.post(url,json=data)
    return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})


def purchase_api(request):
    id =  request.GET.get('ref')
    status = request.GET.get('status')
    draft = PurchaseItems.objects.get(id=id)
    status = Purchase_status(id=status)
    purchase = PurchaseOrder.objects.get(id=draft)
    purchase.status = status
    purchase.save()
    return HttpResponse('success')