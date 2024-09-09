from django.shortcuts import render,redirect,HttpResponse
from sales_orders.models import Sales,Sales_status,Sales_items,Sale_items
from inventory.models import Inventory,Ship_method,Warehouse,Customer
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests

# Create your views here.
def view_sales(request):
    sales = Sales.objects.all()
    return render(request,template_name='sales.html',context={'sales':sales})

def get_sales(request,id):
    sales = Sales.objects.all()
    return render(request,template_name='Sales_next.html',context={'sales':sales})

# making Sales from inventory
def make_sales(request):
    id_list =  request.GET.getlist('item') 
    items = Inventory.objects.filter(id__in=id_list)
    sales_list = []
    warehouse = Warehouse.objects.get(id=1)
    sales = Sales.objects.create(warehouse=warehouse)
    for i in items:
        sales_list.append(Sale_items(
            sales = sales,
            item_id = i,
            price = i.selling_price,
            quantity = 1,
            units = i.units
        ))
    draft = Sales_items.objects.bulk_create(sales_list)
    return redirect(draft_sales,id=sales.id,permanent=True)

def draft_sales(request,id):
    draft = Sales.objects.get(pk=id)
    ship_method = Ship_method.objects.all()
    s = request.GET.get('customer')
    customer = ''
    if s:
        customer = Customer.objects.get(id=s)
        draft.customer = customer
    return render(request,template_name='sales_draft.html',context={'number':id,'item':draft,'customer':customer,'ship_method':ship_method,'customer':customer,'date':datetime.today()})

def sales(request,id):
    draft = Sales_items.objects.get(id=id)
    if Sales.objects.filter(id=draft).exists():
        sales = Sales.objects.get(id=draft)
        return render(request,template_name='sales_next.html',context={'number':id,'items':[draft], 'Sales':sales})
    else:
        if request.method == 'POST':
            supplier = draft.supplier
            bill = request.POST['bill_address']
            ship = request.POST['ship_address']
            sh= request.POST['ship_method']
            ship_method = Ship_method.objects.get(id=sh)
            p_date = request.POST['preferred_date']
            status = Sales_status.objects.get(status='draft')
            Sales = Sales.objects.create(id=draft,warehouse=Warehouse.objects.get(id=1),supplier=supplier,bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=draft.total_price)
            return render(request,template_name='sales_next.html',context={'number':id,'items':[draft], 'Sales':Sales})


def sales_approve(request,id):
    draft = Sales_items.objects.get(id=id)
    status = Sales_status(id=4)
    sales = Sales.objects.get(id=draft)
    sales.status = status
    sales.save()
    url = 'http://localhost:8081/sales/approve'
    data = {
        'ref':sales.id.id,
        'supplier':sales.supplier.name,
        'contact_person':sales.supplier.contact_person,
        'bill_address':sales.bill_address,
        'preferred_shipping_date':sales.preferred_shipping_date.isoformat(),
        "ship_address":sales.ship_address,
        'ship_method':sales.ship_method.method,
        'contact_phone':int(sales.contact_phone),
        'created_date':sales.created_date.isoformat(),
        'total_amount':int(sales.total_amount),
        "items":{'item_id':draft.item_id.id,
                 'price':int(draft.price),
                 'quantity':int(draft.quantity),
                 'units':draft.units}
    }
    requests.post(url,json=data)
    return render(request,template_name='sales_next.html',context={'number':id,'items':[draft], 'Sales':Sales})


def sales_api(request):
    id =  request.GET.get('ref')
    status = request.GET.get('status')
    draft = Sales_items.objects.get(id=id)
    status = Sales_status(id=status)
    sales = Sales.objects.get(id=draft)
    sales.status = status
    sales.save()
    return HttpResponse('success')