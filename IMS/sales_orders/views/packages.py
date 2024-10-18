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

def edit_package_post(request,p):
    try:
        customer = request.POST.get('customer')
        ship = request.POST.get('ship_address')
        quantity = request.POST.getlist('quantity')
        item = request.POST.getlist('item')
        for i in range(len(item)):
            sale = PackageItems.objects.get(id=item[i])
            sale.quantity = quantity[i]
            sale.save()
        p.customer = Customer.objects.get(id=customer)
        p.shipping_address = ship
        if p.status.id > PACKAGE_DRAFT:
            approved = package_approve(request,p.id)
            if approved:
                p.save()
    except PackageItems.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    except Customer.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid customer')
    except ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
    return redirect('get_package',id=p.id)

def edit_package(request,id):
    try:
        p = Package.objects.get(id=id)
        if request.method == 'POST':
            return edit_package_post(request,p)
        else:
            ship_methods = ShipMethod.objects.all()
            customers = Customer.objects.all()
            return render(request,'sales_orders/edit_package.html',{'number':p.id,'items':p.items.all(),'package' :p,'ship_methods':ship_methods,'customers':customers,'sales':p.sales})
    except Package.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    
    
def get_draft(request,sale):
    ship_methods = ShipMethod.objects.all()
    customers = Customer.objects.all()
    items = SalesItems.objects.filter(sales=sale)
    return render(request,'sales_orders/package_draft.html',{'items':items, 'sales':sale,'ship_methods':ship_methods,'customers':customers,'created_date':datetime.now()})

def post_draft(request,sale):
    customer = request.POST.get('customer')
    ship = request.POST.get('ship_address')
    quantity = request.POST.getlist('quantity')
    item = request.POST.getlist('item')
    package_list = []
    items = Inventory.objects.filter(id__in=item)
    if not items:
        return render(request,'404.html',status=404)
    p = Package.objects.create(sales=sale,customer=Customer.objects.get(id=customer),shipping_address=ship,created_at=datetime.now(),status=PackageStatus.objects.get(id=1))
    for i in range(len(items)):
        package_list.append(PackItems(
            package = p,
            item = items[i],
            quantity = quantity[i],
            units = items[i].units
        ))
    PackageItems.objects.bulk_create(package_list)
    return redirect('get_package',p.id)
    
@user_passes_test(specialilst_check)
def package_draft(request,id):
    try:
        sale = Sales.objects.get(id=id)
        if request.method == 'POST':
           return post_draft(request,sale)
        elif sale.status.id == SALE_DRAFT:
            return get_draft(request,sale)
        else:
            return render(request,'404.html',{},status=400)
    except Sales.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    except Customer.DoesNotExist: 
        return HttpResponse('invalid data input')      

@user_passes_test(specialilst_check)
def package(request,id):
    try:
        package = Package.objects.get(id=id)
        try:
            package_approve(request,package.id)
        except requests.exceptions.ConnectionError:
            messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect('get_package',package.id,permanent=True)
    except Package.DoesNotExist:
        return render(request,'404.html',{})  
    
@user_passes_test(specialilst_check)
def package_approve(request,id):
    package = Package.objects.get(id=id)
    if package.status.id <= PACKAGE_PACKED:
        items = package.items.all()
        data = {
            'ref':id,
            'items':items,
            'package': package
        }  
        warehouse = request.w
        url = env('BASE_URL')+f'/{warehouse}/sales/packages/approve/'
        data = PackSerializer(data)
        res = requests.post(url,json=data.data)
        if res.status_code == 201:
            messages.add_message(request,messages.SUCCESS,'Package send to sales team')
            return True
        else:
            messages.add_message(request,messages.ERROR,'Package cant successfully send error occured')
        messages.add_message(request,messages.WARNING,'Invalid package')
        return False
    
  
@user_passes_test(specialilst_check)  
def delete_package(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id == PACKAGE_DRAFT:
            package.delete()
            messages.success(request,f"package {id} deleted successfully")
            return redirect('packages')
        elif package.status.id <= PACKAGE_READY_SHIP:
            warehouse = request.w
            url = env('BASE_URL')+f'{warehouse}/sales/packages/cancel/'
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

def replenish(item):
    if item.on_hand <= item.reorder_point:
        n = Notifications.objects.create(title='Low quantity',
        message=f'Item {item.id} reached reorder point. Click to replinish the item',link = reverse_lazy('make_purchase',args=[item.id]),
        tag='warning')
        n.user.add(User.objects.get(user_type=3))
    
def packed(package):
    sales = package.sales
    items = sales.items.all()
    for i in items:
        i.item.on_hand -= i.quantity
        i.item.save()
        replenish(i.item)
    package.status = PackageStatus.objects.get(id=PACKAGE_PACKED)
    sales.status = SalesStatus.objects.get(id=SALE_PACKED)
    n = Notifications.objects.create(title='Sales team Update: Packed',
    message=f'Package {package.id} status update: Item packed',link = reverse_lazy('get_package',args=[package.id]),
    tag='success')
    n.user.add(User.objects.get(user_type=3))
    package.save()
    sales.save()
    return Response({'data':'successfully updated'},status=201)
    
def ready_to_ship(package):
    package.status = PackageStatus.objects.get(id=PACKAGE_READY_SHIP)
    package.packed_at = datetime.now()
    n = Notifications.objects.create(title='Sales team Update: Ready to ship',
    message=f'Package {package.id} status update: Package ready to ship',link = reverse_lazy('get_package',args=[package.id]),
    tag='success')
    n.user.add(User.objects.get(user_type=3))
    package.save()
    return Response({'data':'successfully updated'},status=201)

@login_not_required
@api_view(["POST"])
def package_api(request):
    try:
        data =  request.data
        package = Package.objects.get(id=data['ref'])
        status = PackageStatus.objects.get(id=data['status'])
        if package.status.id == PACKAGE_DRAFT and status.id == PACKAGE_PACKED:
            return packed(package)
        elif package.status.id == PACKAGE_PACKED and status.id == PACKAGE_READY_SHIP:
            return ready_to_ship(package)
        else:
            return Response({'error':'invalid operation'},status=400)
    except Package.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PackageStatus.DoesNotExist:
        return Response({'error':'invalid status'},status=400)