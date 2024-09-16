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
    sales = Sales.objects.filter(warehouse=request.w)
    return render(request,'sales_orders/sales.html',{'sales':sales})

def get_sales(request,id):
    s = Sales.objects.get(id=id)
    if s:
        return redirect(sales,id=id)
    else:
        return render(request,'404.html',{})

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
    return render(request,'404.html',{})

def get_package(request,id):
    package = Package.objects.get(id=id)
    if sales:
        if package.status == 'draft':
            return redirect(package_draft,id=id.sales.id)
        else:
            return redirect(package,id=id.sales.id)
    return render(request,'404.html',{})



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
        sales = Sales.objects.get(id=id)
        draft = SalesItems.objects.filter(sales=sales.id)
        ship_method = ShipMethod.objects.all()
        customers = Customer.objects.all()
        s = request.GET.get('customer')
        customer = ''
        if s:
            customer = Customer.objects.get(id=s)
        else:
            customer = Customer.objects.first()
        sales.customer = customer
        sales.save()
        return render(request,'sales_orders/sales_draft.html',{'number':id,'items':draft,'customers':customers,'ship_method':ship_method,'customer':customer,'date':datetime.today()})

def sales(request,id):
    sales = Sales.objects.get(id=id)
    if sales:
        draft = SalesItems.objects.filter(sales=sales)
        if sales.status:
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
        else:
            sales.bill_address = request.POST['bill_address']
            sales.ship_address = request.POST['ship_address']
            # total_price = request.POST['total_price']
            sh= request.POST['ship_method'] or 1
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
        ship_method = ShipMethod.objects.all()
        customers = Customer.objects.all()
        if Package(sales=sales):
            p = Package.objects.create(sales=sales,created_at=datetime.now(),status=PackageStatus(id=1),customer=sales.customer,shipping_address=sales.ship_address)
            items = SalesItems.objects.filter(sales=sales)
            return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p,'ship_method':ship_method,'customers':customers})
        else:
            return HttpResponseRedirect('')
    else:
        return HttpResponseRedirect('')

def package(request,id):
    package = Package.objects.get(id=id)
    package.status = PackageStatus(id=1)
    package.save()
    sales = package.sales
    items = SalesItems.objects.filter(sales=sales)
    return render(request,'sales_orders/package.html',{'package':package,'items':items, 'sales':sales})
    
def ship(request,id):
    import random
    track=random.randint(100000000000,9999999999999)
    # pack = request.POST.getlist('package')
    sales = Sales.objects.get(id=id)
    # items = sales.items
    ship = Shipment.objects.get(sales=sales)
    if ship:
        packages = ship.package.all()
        items = sales.items.all()
        return render(request,'sales_orders/ship.html',{'number':id, 'sales':sales,'ship':ship, 'packages':packages, 'items':items})
    else:
        ship = Shipment.objects.create(sales=sales,tracking_number=track,ship_method=sales.ship_method,customer=sales.customer,shipment_address=sales.ship_address)
        # ship.sales.add(sales)
        packages = ship.package.all()
        items = sales.items.all()
        return render(request,'sales_orders/ship.html',{'number':id, 'sales':sales,'ship':ship, 'packages':packages, 'items':items})


from sales_orders.serializer import ShipSerializer
def create_ship(request,id):
    sales = Sales.objects.get(id=id)
    ship = Shipment.objects.get(sales=sales)
    packages = ship.package.all()
    items = sales.items.all()
    ship.status = ShipStatus(id=2)
    ship.save()
    url = 'http://localhost:8081/sales/approve'
    data = ShipSerializer(ship)
    print(data.data)
    # requests.post(url,data)
    # draft = SalesItems.objects.get(sales=sales)
    return redirect(ship,id=id)

    # else:
    #     return HttpResponse('')


from sales_orders.serializer import SalesSerializer
@api_view(['GET'])
def sales_approve(request,id):
    status = SalesStatus(id=4)
    sales = Sales.objects.get(id=id)
    draft = SalesItems.objects.get(sales=sales)
    sales.status = status
    sales.save()
    url = 'http://localhost:8081/sales/approve'
    data = SalesSerializer(sales,items=draft)
    print(data.data)
    # for i in draft:
    #     items['item']=i.item.name
    #     items['price'] = i.price
    #     items['quantity'] = i.quantity
    #     items['un']
    # data = {
    #     'ref':sales.id,
    #     'customer':sales.customer.name,
    #     'contact_person':sales.sales_person,
    #     'bill_address':sales.bill_address,
    #     'preferred_shipping_date':sales.preferred_shipping_date.isoformat(),
    #     "ship_address":sales.ship_address,
    #     'ship_method':sales.ship_method.method,
    #     'contact_phone':int(sales.contact_phone),
    #     'created_date':sales.created_date.isoformat(),
    #     'total_amount':int(sales.total_amount),
    #     "items":{'item_id':draft.item.id,
    #              'price':int(draft.price),
    #              'quantity':int(draft.quantity),
    #              'units':draft.units}
    # }
    requests.post(url,json=data)
    return render(request,'sales_next.html',{'number':id,'items':[draft], 'Sales':Sales})


@api_view(['post'])
def sales_api(request):
    data = request.data
    id =  data['ref']
    status = data['status']
    draft = Sales.objects.get(id=id)
    status = SalesStatus(id=status)
    draft.status = status
    draft.save()
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