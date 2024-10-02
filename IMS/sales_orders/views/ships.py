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
from core.utils import specialilst_check,user_passes_test
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

def date_filter(date,queryset):
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        queryset = queryset.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        queryset = queryset.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        queryset = queryset.filter(updated__year=year)
    return queryset



def view_ships(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    ships = Shipment.objects.filter(sales__warehouse=request.w).order_by(orderby)
    ships = date_filter(date,ships)
    return render(request,'sales_orders/ships.html',{'ships':ships})


def get_ship(request,id):
    try:      
        sh = Shipment.objects.get(id=id)
        return redirect(ship,id=sh.sales.id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    except AttributeError:
        return render(request,'404.html',{})
    

def ship(request,id):
    try:
        sale = Sales.objects.get(id=id)
        shiplist = Shipment.objects.filter(sales=sale)
        if request.method == 'POST' and specialilst_check and sale.status.id == SALE_PACKED:
            pack = request.POST.getlist('package')
            packages = Package.objects.filter(id__in=pack)
            if shiplist:
                [sh,] = shiplist
            else:            
                status = ShipStatus(id=READY_TO_SHIP)
                import random
                track=random.randint(100000000000,9999999999999)
                sh = Shipment.objects.create(status=status, sales=sale,tracking_number=track,ship_method=sale.ship_method,customer=sale.customer,shipment_address=sale.ship_address)
                # ship.sales.add(sales)
                packages.update(ship=sh,status=PackageStatus(id=PACKAGE_READY_SHIP))
            items = sale.items.all()
            return render(request,'sales_orders/ship.html',{'number':id, 'sales':sale,'ship':sh, 'packages':packages, 'items':items})
        # items = sales.items
        else:
            if shiplist:
                [sh,] = shiplist
                packages = sh.package.all()
                items = sale.items.all()
                return render(request,'sales_orders/ship.html',{'number':id, 'sales':sale,'ship':sh, 'packages':packages, 'items':items})
            else:
                return render(request,'404.html',{})
                
    except Sales.DoesNotExist:
        return render(request,'404.html',{})



@user_passes_test(specialilst_check)
def cancel_ship(request,id):
    try:
        sh = Shipment.objects.get(id=id)
        if sh.status.id < CUSTOMER_RECEIVED:
            sh.status = ShipStatus.objects.get(status='cancelled')
            url = env('BASE_URL')+'/sales/ships/cancel/'
            requests.post(url,json={'ref':sh.status.id})
            sh.save()
            messages.info(request,f"shipment {sh.id} cancelled")
            return redirect('ships')
        else:
            messages.warning(request,f"shipment {sh.id} cant be cancelled already received")
            return redirect('get_ship',id=id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    
    

@user_passes_test(specialilst_check)
def create_ship(request,id):
    try:
        sales = Sales.objects.get(id=id)
        shipment = Shipment.objects.get(sales=sales)
        if sales.status.id == SALE_PACKED and shipment.status.id == READY_TO_SHIP:
            packages = shipment.package.all()
            items = sales.items.all()
            data = {'ref':shipment.id,
                    'shipment':shipment,
                    'packages':packages,
                    'items':items}
            url = env('BASE_URL')+'/sales/ships/approve/'
            shipment.status = ShipStatus(id=SENT_TO_FLEET)
            shipment.save()
            serializer = ShipSerializer(data)
            requests.post(url,json=serializer.data)
            messages.add_message(request,messages.SUCCESS,'Successfully send for approval')
            return redirect(ship,id=id)
        elif sales.status.id >= SALE_SHIPPED:
            messages.add_message(request,messages.WARNING,'Already shiped!')
        elif sales.status.id < SALE_PACKED:
            messages.add_message(request,messages.WARNING,'No packages to be shipped!')   
        else:
            messages.add_message(request,messages.WARNING,'Already sent for shipment')   
        return redirect(ship,id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    except Shipment.DoesNotExist:
        return HttpResponseRedirect('')
    except requests.exceptions.ConnectionError:
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
        st = ''
        if int(status.id) == SENT_TO_CARRIER:
            pass
        elif int(status.id) == CARRIER_PICKED:
            sales.status = SalesStatus(SALE_SHIPPED)
            package.update(status=PackageStatus(PACKAGE_SHIPPED))
        elif int(status.id) == CUSTOMER_RECEIVED:
            sales.status = SalesStatus(SALE_DELIVERED)
        else:
            n = Notifications.objects.create(title='Sales team Update Error',
            message=f'Ship order {data['ref']} update error ',link = reverse_lazy('get_ship',args=[data['ref']]),
            tag='danger')
            n.user.add(User.objects.get(user_type=3))
            return Response({'data':'cant be updated'},status=403)
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