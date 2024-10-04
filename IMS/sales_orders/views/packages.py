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
        return render(request,'sales_orders/package.html',{'package':p,'items':p.items.all(), 'sales':sale,'created_date':p.created_at})
    except Package.DoesNotExist:
        return render(request,'404.html',{},status=404)


def edit_package(request,id):
    try:
        p = Package.objects.get(id=id)
        if request.method == 'POST':
            customer = request.POST.get('customer')
            ship = request.POST.get('ship_address')
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            for i in range(len(item)):
                sale = PackageItems.objects.get(id=item[i])
                sale.quantity = quantity[i]
                sale.save()
            try:
                p.customer = Customer.objects.get(id=customer)
                p.shipping_address = ship
                approved = package_approve(request,p.id)
                if approved:
                    p.save()
            except Customer.DoesNotExist:
                messages.add_message(request,messages.ERROR,'Invalid customer')
            except ConnectionError:
                messages.add_message(request,messages.ERROR,'Cant connect to the server')
            return render(request,'sales_orders/package.html',{'package':p,'items':p.items.all(), 'sales':p.sales})
        else:
            ship_methods = ShipMethod.objects.all()
            customers = Customer.objects.all()
            return render(request,'sales_orders/edit_package.html',{'number':p.id,'items':p.items.all(),'package' :p,'ship_methods':ship_methods,'customers':customers,'sales':p.sales})
    except Package.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    except PackageItems.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    

    
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
            if items:
                try:
                    p = Package.objects.create(sales=sale,customer=Customer.objects.get(id=customer),shipping_address=ship,created_at=datetime.now(),status=PackageStatus.objects.get(id=1))
                except Customer.DoesNotExist: 
                   return HttpResponse('invalid data input')      
                for i in range(len(items)):
                    package_list.append(PackItems(
                        package = p,
                        item = items[i],
                        quantity = quantity[i],
                        units = items[i].units
                    ))
                PackageItems.objects.bulk_create(package_list)
                return render(request,'sales_orders/package.html',{'package':p,'items':p.items.all(), 'sales':sale,'created_date':datetime.now()})
            else:
               return render(request,'404.html',status=404)
        elif sale.status.id == SALE_DRAFT:
            ship_methods = ShipMethod.objects.all()
            customers = Customer.objects.all()
            items = SalesItems.objects.filter(sales=sale)
            return render(request,'sales_orders/package_draft.html',{'items':items, 'sales':sale,'ship_methods':ship_methods,'customers':customers,'created_date':datetime.now()})
        else:
            return render(request,'404.html',{},status=400)
    except Sales.DoesNotExist:
        return  render(request,'404.html',{},status=404)

@user_passes_test(specialilst_check)
def package(request,id):
    try:
        package = Package.objects.get(id=id)
        try:
            package_approve(request,package.id)
        except ConnectionError:
            messages.add_message(request,messages.ERROR,'Cant connect to the server')
        sales = package.sales
        items = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/package.html',{'package':package,'items':items, 'sales':sales})
    except Package.DoesNotExist:
        return render(request,'404.html',{})  
    
@user_passes_test(specialilst_check)
def package_approve(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id <= PACKAGE_PACKED:
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
                return True
            else:
                messages.add_message(request,messages.ERROR,'Package cant successfully send error occured')
            messages.add_message(request,messages.WARNING,'Invalid package')
            return False
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
        return render(request,'404.htnl',{},status=404)
    except requests.ConnectionError:
        messages.error(request,"Cant connect to the server!")
        return redirect(get_package,id=id)
    

@login_not_required
@api_view(["POST"])
def package_api(request):
    try:
        data =  request.data
        package = Package.objects.get(id=data['ref'])
        status = PackageStatus.objects.get(id=data['status'])
        sales = package.sales
        items = sales.items.all()
        if package.status.id == PACKAGE_DRAFT and status.id == PACKAGE_PACKED:
            for i in items:
                i.item.on_hand -= i.quantity
                i.item.save()
            package.status = PackageStatus.objects.get(id=PACKAGE_PACKED)
            sales.status = SalesStatus.objects.get(id=SALE_PACKED)
            n = Notifications.objects.create(title='Sales team Update: Packed',
            message=f'Package {data['ref']} status update: Item packed',link = reverse_lazy('get_package',args=[data['ref']]),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
        elif package.status.id == PACKAGE_PACKED and status.id == PACKAGE_READY_SHIP:
            package.status = PackageStatus.objects.get(id=PACKAGE_READY_SHIP)
            package.packed_at = datetime.now()
            n = Notifications.objects.create(title='Sales team Update: Ready to ship',
            message=f'Package {data['ref']} status update: Package ready to ship',link = reverse_lazy('get_package',args=[data['ref']]),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
        else:
            return Response({'error':'invalid operation'},status=400)
        package.save()
        sales.save()
        return Response({'data':'successfully updated'},status=201)
    except Package.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PackageStatus.DoesNotExist:
        return Response({'error':'invalid status'},status=400)