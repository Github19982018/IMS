from django.shortcuts import redirect,HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse as render
from sales_orders.models import Sales,SalesStatus,SalesItems,SaleItems,Package,PackageStatus,ShipStatus,Shipment
from inventory.models import Inventory,ShipMethod
from warehouse.models import Warehouse
from customer.models import Customer
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
from django.contrib import messages

# Create your views here.
def view_sales(request):
    sales = Sales.objects.all()
    return render(request,'sales_orders/sales.html',{'sales':sales})

def get_sales(request,id):
    return redirect(sales,id=id)

# making Sales from inventory
def make_sales(request):
    if request.method == 'POST':
        id_list =  request.POST.getlist('item') 
        if len(id_list)>=1:
            items = Inventory.objects.filter(id__in=id_list)
            w = request.w
            warehouse = Warehouse.objects.get(id=w)
            # warehouse = Warehouse.objects.all()
            sales = Sales.objects.create(warehouse=warehouse)
            sales_list = []
            for i in items:
                sales_list.append(SaleItems(
                    sales = sales,
                    item = i,
                    price = i.selling_price,
                    quantity = 1,
                    units = i.units
                ))
            draft = SalesItems.objects.bulk_create(sales_list)
            return redirect(draft_sales,id=sales.id)
        else:
            return render(request,'404.html',{})
    else:
        HttpResponse('')

def get_package(request,id):
    sales = Sales.objects.get(id=id)
    if sales.package == 'draft':
        return redirect(package_draft,id=id)
    else:
        return redirect(package,id=id)



def draft_sales(request,id):
    if request.method == 'POST':
        quantity = request.POST.getlist('quantity')
        item = request.POST.getlist('item')
        for i in range(len(item)):
            sale = SalesItems.objects.get(id=item[i])
            sale.quantity = quantity[i]
            sale.save()
            return HttpResponseRedirect('')
    else:
        draft = SalesItems.objects.filter(sales=id)
        ship_method = ShipMethod.objects.all()
        customers = Customer.objects.all()
        s = request.GET.get('customer')
        customer = ''
        if s:
            customer = Customer.objects.get(id=s)
        else:
            customer = Customer.objects.first()
        for i in draft:
            i.customer = customer
            i.save()
        return render(request,'sales_orders/sales_draft.html',{'number':id,'items':draft,'customers':customers,'ship_method':ship_method,'customer':customer,'date':datetime.today()})

def sales(request,id):
    sales = Sales.objects.get(id=id)
    if sales:
        draft = SalesItems.objects.filter(sales=sales)
        if sales.status:
            return render(request,'sales_orders/sale.html',{'number':id,'items':[draft], 'sales':sales})
        else:
                sales.customer = draft.first().customer
                sales.bill_address = request.POST['bill_address']
                sales.ship_address = request.POST['ship_address']
                # total_price = request.POST['total_price']
                sh= request.POST['ship_method']
                sales.ship_method = ShipMethod.objects.get(id=sh)
                p_date = request.POST['preferred_date']
                sales.preferred_shipping_date = datetime.strptime(p_date,'%d/%m/%Y, %I:%M:%S %p')
                sales.status = SalesStatus.objects.get(status='draft')
                sales.warehouse = Warehouse.objects.get(id=request.w)
                sales.save()
                return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    else:
        return  render(request,'404.html',{})
    
def package_draft(request,id):
    sales = Sales.objects.get(id=id)
    if sales:
        if Package(sales=sales):
            p = Package.objects.create(sales=sales,created_at=datetime.now(),status=PackageStatus(id=1),customer=sales.customer,shipping_address=sales.ship_address)
            items = SalesItems.objects.filter(sales=sales)
            return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p})
        else:
            return HttpResponseRedirect('')
    else:
        return HttpResponseRedirect('')

def package(request,id):
    sales = Sales.objects.get(id=id)
    # sales.status = Sales_status(id=2)
    # sales.save()
    items = SalesItems.objects.filter(sales=sales)
    return render(request,'sales_orders/package.html',{'number':id,'items':items, 'sales':sales})
    
def ship(request,id):
    import random
    track=random.randint(100000000000,9999999999999)
    pack = request.POST.getlist('package')
    sales = Sales.objects.get(id=id)
    # items = Sale_items.objects.get(sales=sales)
    ship = Shipment.objects.create(sales=sales,tracking_number=track,ship_method=sales.ship_method,customer=sales.customer,shipment_address=sales.ship_address)
    # ship.sales.add(sales)
    packages = Package.objects.filter(pk__in=pack).update(ship=ship)
    return render(request,'sales_orders/ship.html',{'number':id, 'sales':sales,'ship':ship, 'packages':packages})

@api_view(['GET'])
def sales_approve(request,id):
    draft = SalesItems.objects.get(id=id)
    status = SalesStatus(id=4)
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
    return render(request,'sales_next.html',{'number':id,'items':[draft], 'Sales':Sales})


@api_view(['post'])
def sales_api(request):
    id =  request.POST['ref']
    status = request.POST['status']
    draft = SalesItems.objects.get(id=id)
    status = SalesStatus(id=status)
    sales = Sales.objects.get(id=draft)
    sales.status = status
    sales.save()
    return HttpResponse('success')

@api_view(["POST"])
def package_api(request):
    id =  request.POST['ref']
    status = request.POST['status']
    draft = Package.objects.get(id=id)
    status = PackageStatus(id=status)
    sales = draft.sales
    draft.status = status
    sales.staus = 2
    draft.save()
    sales.save()
    messages.add_message(request,messages.INFO,f"package {id}: {status}")
    return HttpResponse('success')

@api_view(["POST"])
def ship_api(request):
    id =  request.POST['ref']
    status = request.POST['status']
    draft = Shipment.objects.get(id=id)
    status = ShipStatus(id=status)
    sales = draft.sales
    draft.status = status
    if status == 2:
        sales.status = 3
    elif status == 3:
        sales.status = 4
    draft.save()
    sales.save()
    messages.add_message(request,messages.INFO,f"package {id}: {status}")
    return HttpResponse('success')