from django.shortcuts import redirect,HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse as render
from sales_orders.models import Sales,PackageItems,PackItems,SalesStatus,SalesItems,SaleItems,Package,PackageStatus,ShipStatus,Shipment
from inventory.models import Inventory,ShipMethod
from warehouse.models import Warehouse
from customer.models import Customer
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import APIException
import requests
from django.contrib import messages
from core.utils import specialilst_check,user_passes_test,date_filter
from sales_orders.serializer import PackSerializer,ShipSerializer
import environ
from django.contrib.auth.decorators import login_not_required
from core.models import Notifications,User
from django.urls import reverse_lazy


env = environ.Env()
environ.Env.read_env()


READY_TO_SHIP = 0
SENT_TO_FLEET = 1
SENT_TO_CARRIER =2
CARRIER_PICKED = 3
CUSTOMER_RECEIVED = 4
SHIP_CANCELLED = 5

SALE_DRAFT = 1
SALE_PACKED = 2
SALE_SHIPPED = 3
SALE_DELIVERED = 4
PAYED = 5
SALE_CANCELLED = 6

PACKAGE_DRAFT = 1
PACKAGE_PACKED = 2
PACKAGE_READY_SHIP = 3
PACKAGE_SHIPPED = 4




def view_ships(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    ships = Shipment.objects.filter(sales__warehouse=request.w).order_by(orderby)
    ships = date_filter(date,ships)
    return render(request,'sales_orders/ships.html',{'ships':ships})


def get_ship(request,id):
    try:      
        sh = Shipment.objects.get(id=id)
        sale = sh.sales
        packages = sh.package.all()
        items = []
        for i in packages:
            items += i.items.all() 
        return render(request,'sales_orders/ship.html',{'number':id, 'sales':sale,'ship':sh, 'packages':packages, 'items':items})
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    
def ship_object_create(sale,packages):
    status = ShipStatus.objects.get(id=READY_TO_SHIP)
    import random
    track=random.randint(100000000000,9999999999999)
    sh = Shipment.objects.create(status=status, sales=sale,tracking_number=track,ship_method=sale.ship_method,customer=sale.customer,shipment_address=sale.ship_address)
    # ship.sales.add(sales)
    packages.update(ship=sh)
    return sh

def ship(request,id):
    try:
        sale = Sales.objects.get(id=id)
        shiplist = Shipment.objects.filter(sales=sale)
        if request.method == 'POST' and specialilst_check(request.user): 
            if sale.status.id == SALE_PACKED:
                pack = request.POST.getlist('package')
                packages = Package.objects.filter(id__in=pack)
                if shiplist:
                    sh = shiplist.last()
                    if sh.cancel or sh.status.id == SHIP_CANCELLED: 
                        ship_object_create(sale,packages)
                else:            
                    sh = ship_object_create(sale,packages)
                return redirect('get_ship',sh.id)
        # items = sales.items
        if request.method == "GET":
            if shiplist:
                sh = shiplist.last()
                packages = sh.package.all()
                items = sale.items.all()
                return render(request,'sales_orders/ship.html',{'number':id, 'sales':sale,'ship':sh, 'packages':packages, 'items':items})
        return render(request,'404.html',{})
                
    except Sales.DoesNotExist:
        return render(request,'404.html',{})



@user_passes_test(specialilst_check)
def cancel_ship(request,id):
    try:
        sh = Shipment.objects.get(id=id)
        if sh.status.id < CUSTOMER_RECEIVED and not sh.cancel:
            sh.status = ShipStatus.objects.get(status='cancelled')
            warehouse = request.w
            url = env('BASE_URL')+f'/{warehouse}/sales/ships/cancel/'
            requests.post(url,json={'ref':sh.id})
            sh.sales.status = SalesStatus.objects.get(id=SALE_PACKED)
            packages = sh.package.all()
            packages.update(status=PackageStatus.objects.get(id=PACKAGE_READY_SHIP),ship=None)
            sh.save()
            sh.sales.save()
            messages.info(request,f"shipment {sh.id} cancelled")
            return redirect('ships')
        else:
            messages.warning(request,f"shipment {sh.id} cant be cancelled: either delivered or already cancelled")
            return redirect('get_ship',id=id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    
def shipped(shipment,warehouse):
    packages = shipment.package.all()
    items = shipment.sales.items.all()
    data = {'ref':shipment.id,
            'shipment':shipment,
            'packages':packages,
            'items':items}
    url = env('BASE_URL')+f'/{warehouse}/sales/ships/approve/'
    if shipment.status.id <= READY_TO_SHIP:
        shipment.status = ShipStatus.objects.get(id=SENT_TO_FLEET)
        shipment.save()
    serializer = ShipSerializer(data)
    try:
        requests.post(url,json=serializer.data)
    except requests.exceptions.ConnectionError:
        raise(ConnectionError)

@user_passes_test(specialilst_check)
def create_ship(request,id):
    try:
        sales = Sales.objects.get(id=id)
        shipment = Shipment.objects.get(sales=sales)
        warehouse = request.w
        if shipment.cancel: 
            messages.add_message(request,messages.SUCCESS,'cancelled order')
        elif sales.status.id == SALE_PACKED:
            if shipment.status.id == READY_TO_SHIP:
                shipped(shipment,warehouse)
                messages.add_message(request,messages.SUCCESS,'Successfully send for approval')
            elif shipment.status.id > READY_TO_SHIP:
                shipped(shipment,warehouse)
                messages.add_message(request,messages.WARNING,'Sent shipment for update')   
        elif sales.status.id >= SALE_SHIPPED:
            messages.add_message(request,messages.WARNING,'Already shiped!')
        elif sales.status.id < SALE_PACKED:
            messages.add_message(request,messages.WARNING,'No packages to be shipped!')   
        return redirect('get_ship',id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    except ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(ship,id=id)



@login_not_required
@api_view(["POST"])
def ship_api(request):
    try:
        data = request.data
        draft = Shipment.objects.get(id=data['ref'])
        status = ShipStatus.objects.get(id=data['status'])
        package = draft.package.all()
        sales = draft.sales
        draft.status = status
        draft.shipment_date = datetime.now()
        st = ''
        if draft.cancel:    
          return  notification_error(data['ref'])
        if int(status.id) == SENT_TO_CARRIER:
            pass
        elif int(status.id) == CARRIER_PICKED:
            sales.status = SalesStatus.objects.get(id=SALE_SHIPPED)
            package.update(status=PackageStatus.objects.get(id=PACKAGE_SHIPPED))
        elif int(status.id) == CUSTOMER_RECEIVED:
            sales.status = SalesStatus.objects.get(id=SALE_DELIVERED)
        else:
          return  notification_error(data['ref'])
        draft.save()
        sales.save()
        n = Notifications.objects.create(title='Sales team Update',
        message=f'Ship order {data['ref']} status update: {status.status}',link = reverse_lazy('get_ship',args=[data['ref']]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except Shipment.DoesNotExist:
            return HttpResponse({'error':'order does not exist'},status=404)
    except ShipStatus.DoesNotExist:
            return HttpResponse({f'error':'invalid data: status:{status}'},status=404)
        
    
def payed(sale):
    status = SalesStatus.objects.get(id=PAYED)
    sale.status = status
    sale.save()
    n = Notifications.objects.create(title='Sales team Update',
    message=f'Sales order {sale.id} status update: Payed by customer',link = reverse_lazy('get_sale',args=[sale.id]),
    tag='success')
    n.user.add(User.objects.get(user_type=3))
    return Response({'data':'successfully updated'},status=201)

def notification_error(id):
    n = Notifications.objects.create(title='Sales team Update Error',
    message=f'Sales order {id} Update error',link = reverse_lazy('get_sale',args=[id]),
    tag='danger')
    n.user.add(User.objects.get(user_type=3))
    return Response({'error':'invalid status'},status=403)

@login_not_required
@api_view(['POST'])
def sales_api(request):
    try:
        data = request.data
        id =  data['ref']
        status = data['status']
        draft = Shipment.objects.get(id=id)
        sale = draft.sales
        if int(status) == PAYED:
            return payed(sale)
        else:
            return notification_error(sale.id)
    except Shipment.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except SalesStatus.DoesNotExist:
        return Response({'error':'Invalid status'},status=400)