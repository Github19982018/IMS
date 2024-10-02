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

def view_packages(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    packages = Package.objects.filter(sales__warehouse=request.w).order_by(orderby)
    packages = date_filter(date,packages)
    return render(request,'sales_orders/packages.html',{'packages':packages})


def get_package(request,id):
    try:      
        p = Package.objects.get(id=id)
        sale = p.sales
        return render(request,'sales_orders/package.html',{'package':p,'items':p.items.all(), 'sales':sale,'created_date':datetime.now()})
    except Package.DoesNotExist:
        return render(request,'404.html',{})
    except AttributeError:
        return render(request,'404.html',{})


def edit_package(request,id):
    try:
        p = Package.objects.get(id=id)
        if request.method == 'POST':
            customer = request.POST.get('customer')
            ship = request.POST.get('ship_address')
            p.customer = Customer(id=customer)
            p.ship = ship
            p.save()
            sale = p.sales
            return render(request,'sales_orders/package.html',{'package':p,'items':sale.items.all(), 'sales':sale})
        else:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            customer = p.customer
            ship_method= p.shipping_address

            return render(request,'sales_orders/edit_package.html',{'number':p.id,'items':package.items.all(),'package' :p,'ship_method':ship_method,'customers':customers})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def package_draft(request,id):
    try:
        sale = Sales.objects.get(id=id)
        if request.method == 'POST':
            customer = request.POST.get('customer')
            ship = request.POST.get('ship_address')
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            package_list = []
            items = Inventory.objects.filter(id__in=item)
            p = Package.objects.create(sales=sale,customer=Customer(id=customer),shipping_address=ship,created_at=datetime.now(),status=PackageStatus(id=1))
            for i in range(len(items)):
                package_list.append(PackItems(
                    package = p,
                    item = items[i],
                    quantity = quantity[i],
                    units = items[i].units
                ))
            PackageItems.objects.bulk_create(package_list)
            print(p.items.all())
            return render(request,'sales_orders/package.html',{'package':p,'items':p.items.all(), 'sales':sale,'created_date':datetime.now()})
        elif sale.status.id < 5:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            items = SalesItems.objects.filter(sales=sale)
            return render(request,'sales_orders/package_draft.html',{'items':items, 'sales':sale,'ship_method':ship_method,'customers':customers})
        else:
            return render(request,'404.html',{})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})

@user_passes_test(specialilst_check)
def package(request,id):
    try:
        package = Package.objects.get(id=id)
        package_approve(request,package.id)
        sales = package.sales
        items = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/package.html',{'package':package,'items':items, 'sales':sales})
    except Package.DoesNotExist:
        return render(request,'404.html',{})  
    except ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return HttpResponseRedirect('/')
    
@user_passes_test(specialilst_check)
def package_approve(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id <PACKAGE_PACKED:
            items = package.sales.items.all()
            data = {
                'ref':id,
                'items':items,
                'package': package
            }  
            url = env('BASE_URL')+'/sales/packages/approve/'
            data = PackSerializer(data)
            res = requests.post(url,json=data.data)
            if res.status_code == 201:
                messages.add_message(request,messages.SUCCESS,'Package send to sales team')
            else:
                messages.add_message(request,messages.ERROR,'Package cant successfully send error occured')
    except Sales.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
    except SalesItems.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
    except requests.exceptions.ConnectionError:
        raise(ConnectionError)
  
@user_passes_test(specialilst_check)  
def delete_package(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id == PACKAGE_DRAFT:
            package.delete()
            messages.success(request,f"package {id} deleted successfully")
            return redirect('packages')
        elif package.status.id <= PACKAGE_READY_SHIP:
            url = env('BASE_URL')+'/sales/packages/cancel/'
            requests.post(url,json={'ref':[package.id]})
            package.delete()
            messages.success(request,f"package {id} deleted successfully")
            return redirect('packages')
        else:
            messages.warning(request,"Package can't be deleted")
            return redirect(get_package,id=id)
    except Package.DoesNotExist:
        return render(request,'404.htnl',{})
    except requests.ConnectionError:
        messages.error(request,"Cant connect to the server!")
        return redirect(get_package,id=id)
    

@login_not_required
@api_view(["POST"])
def package_api(request):
    try:
        data =  request.data
        print(data['ref'])
        package = Package.objects.get(id=data['ref'])
        status = PackageStatus.objects.get(id=data['status'])
        sales = package.sales
        items = sales.items.all()
        if status.id == PACKAGE_PACKED:
            for i in items:
                i.item.on_hand -= i.quantity
                i.item.save()
            package.status = PackageStatus(PACKAGE_PACKED)
            sales.status = SalesStatus(SALE_PACKED)
        elif status.id == PACKAGE_READY_SHIP:
            package.status = PackageStatus(PACKAGE_READY_SHIP)
        package.save()
        sales.save()
        n = Notifications.objects.create(title='Sales team Update',
        message=f'Package {data['ref']} status update: Item packed',link = reverse_lazy('get_package',args=[data['ref']]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except Package.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)