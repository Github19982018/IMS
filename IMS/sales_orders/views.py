from django.shortcuts import redirect,HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse as render
from sales_orders.models import Sales,SalesStatus,SalesItems,SaleItems,Package,PackageStatus,ShipStatus,Shipment
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

# Create your views here.
def view_sales(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    sales = Sales.objects.filter(warehouse=request.w).order_by(orderby)
    sales = date_filter(date, sales)
    return render(request,'sales_orders/sales.html',{'sales':sales})

def view_packages(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    packages = Package.objects.filter(sales__warehouse=request.w).order_by(orderby)
    packages = date_filter(date,packages)
    return render(request,'sales_orders/packages.html',{'packages':packages})


def view_ships(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    ships = Shipment.objects.filter(sales__warehouse=request.w).order_by(orderby)
    ships = date_filter(date,ships)
    return render(request,'sales_orders/ships.html',{'ships':ships})

def get_sales(request,id):
    try:
        sales = Sales.objects.get(id=id)
        draft = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    except Sales.DoesNotExist:
        return render(request,'404.html',{})



def get_package(request,id):
    try:      
        pack = Package.objects.get(id=id)
        # pack = sale.package.first()
        if pack.status.status == 'draft':
            return redirect(package_draft,id=pack.sales.id)
        else:
            return redirect(package,id=pack.sales.id)
    except Package.DoesNotExist:
        return render(request,'404.html',{})
    
def get_ship(request,id):
    try:      
        sh = Shipment.objects.get(id=id)
        return redirect(ship,id=sh.sales.id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})


@user_passes_test(specialilst_check)
def draft_sales(request):
    ship_method = ShipMethod.objects.all()
    customers = Customer.objects.all()
    if request.method == 'POST':
        id_list =  request.POST.getlist('item') 
        if id_list:
            items = Inventory.objects.filter(id__in=id_list)
            customer = customers.first()
            return render(request,'sales_orders/sales_draft.html',{'items':items,'customer':customer,'customers':customers,'ship_method':ship_method,'date':datetime.today()})
        else:
            messages.add_message(request,messages.WARNING,'please select an item to order')    
            return redirect('inventories')

@user_passes_test(specialilst_check)
def save_items(request):
    try:
        if request.method == 'POST':
            warehouse = Warehouse.objects.get(id=request.w)
            sale = Sales.objects.create(warehouse=warehouse,customer=Customer.objects.first())
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            sales_list = []
            items = Inventory.objects.filter(id__in=item)
            total = 0
            for i in range(len(items)):
                sales_list.append(SaleItems(
                    sales = sale,
                    item = items[i],
                    price = items[i].selling_price,
                    quantity = quantity[i],
                    units = items[i].units
                ))
                total += float(quantity[i])*float(items[i].selling_price)
            sale.total_amount = total
            sale.save()
            draft = SalesItems.objects.bulk_create(sales_list)
            return sales(request,sale.id)
        else:
            sale = Sales.objects.get(id=id)
            return redirect(sales,id=sale.id,permanent=True)
    except Customer.DoesNotExist:
        pass
    except Sales.DoesNotExist:
        return render(request,'404.html',{})


        
@user_passes_test(specialilst_check)
def sales(request,id):
    try: 
        if request.method == 'POST':
            sales = Sales.objects.get(id=id)
            draft = SalesItems.objects.filter(sales=sales)
            sales.bill_address = request.POST['bill_address']
            sales.ship_address = request.POST['ship_address']
            customer = request.POST['customer']
            sales.customer = Customer.objects.get(id=customer)
            # sales.total_price = request.POST['total_price']
            sh= request.POST['ship_method']
            sales.ship_method = ShipMethod.objects.get(id=sh)
            p_date = request.POST['preferred_date']
            sales.preferred_shipping_date = datetime.strptime(p_date,'%m/%d/%Y, %I:%M:%S %p')
            sales.status = SalesStatus.objects.get(status='draft')
            sales.warehouse = Warehouse.objects.get(id=request.w)
            sales.save()
            print(sales.ship_method)
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})
    except SalesItems.DoesNotExist:
        return  render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def edit_sales(request,id):
    try:
        sale = Sales.objects.get(id=id)
        if sale.status.id < 5:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            items = SalesItems.objects.filter(sales=sale)
            return render(request,'sales_orders/sales_edit.html',{'items':items,'sales':sale,'ship_method':ship_method, 'customers':customers})
        else:
            return render(request,'404.html',{})
    except Sales.DoesNotExist:
        return render(request,'404.html',{})


@user_passes_test(specialilst_check)
def package_draft(request,id):
    try:
        sales = Sales.objects.get(id=id)
        if sales.status.id < 5:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            items = SalesItems.objects.filter(sales=sales)
            p = Package.objects.get(sales=sales)
            return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p,'ship_method':ship_method,'customers':customers})
        else:
            return render(request,'404.html',{})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})
    except Package.DoesNotExist:
        p = Package.objects.create(sales=sales,created_at=datetime.now(),status=PackageStatus(id=1),customer=sales.customer,shipping_address=sales.ship_address)
        return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p,'ship_method':ship_method,'customers':customers})

@user_passes_test(specialilst_check)
def package(request,id):
    try:
        sales = Sales.objects.get(id=id)
        package = Package.objects.get(sales=sales)
        package_approve(request,package.id)
        sales = package.sales
        items = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/package.html',{'package':package,'items':items, 'sales':sales})
    except Package.DoesNotExist:
        return render(request,'404.html',{})  
    
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
            status = PackageStatus(id=2)
            package.status = status
            requests.post(url,json=data.data)
            package.save()
            messages.add_message(request,messages.SUCCESS,'Package send to sales team')
    except Sales.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
    except SalesItems.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
    
  
@user_passes_test(specialilst_check)  
def delete_package(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id <= PACKAGE_READY_SHIP:
            url = env('BASE_URL')+'/sales/packages/cancel/'
            requests.post(url,json={'ref':[package.id]})
            package.delete()
            messages.success(request,f"package {id} deleted successfully")
            return redirect('packages')
        else:
            messages.warning(request,"Pakage can't be deleted")
            return redirect(get_package,id=id)
    except Package.DoesNotExist:
        return render(request,'404.htnl',{})
    

def ship(request,id):
    try:
        sale = Sales.objects.get(id=id)
        shiplist = Shipment.objects.filter(sales=sale)
        if request.method == 'POST' and specialilst_check:
            if shiplist:
                [sh,] = shiplist
            else:            
                status = ShipStatus(id=READY_TO_SHIP)
                import random
                track=random.randint(100000000000,9999999999999)
                sh = Shipment.objects.create(status=status, sales=sale,tracking_number=track,ship_method=sale.ship_method,customer=sale.customer,shipment_address=sale.ship_address)
            # ship.sales.add(sales)
            pack = request.POST.getlist('package')
            packages = Package.objects.filter(id__in=pack)
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
            return render(request,'sales_orders/ships.html',{})
        else:
            messages.warning(request,f"shipment {sh.id} cant be cancelled already received")
            return redirect('get_ship',id=id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def cancel_sales(request,id):
    try:
        s = Sales.objects.get(id=id)
        if not s.status:
            s.delete()
            messages.info(request,f"sales order deleted")
            return redirect('sales')
        elif s.status.id < SALE_SHIPPED:
            s.status = SalesStatus.objects.get(status='cancelled')
            p = s.package.all()
            url = env('BASE_URL')+'/sales/packages/cancel/'
            res = requests.post(url,json={'ref':list(p.values_list('id',flat=True))})
            if res.status_code == 201:
                p.delete()
            sh = s.shipment
            url = env('BASE_URL')+'/sales/ships/cancel/'
            res = requests.post(url,json={'ref':[sh.id]})
            if res.status_code == 201:
                sh.status = ShipStatus(status='cancelled')
                sh.save()
            s.save()
            messages.info(request,f"sales {s.id} cancelled")
            return render(request,'sales_orders/sales.html',{})
     
        else:
            messages.warning(request,f"sales {s.id} cant be cancelled")
            return redirect('get_sale',id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    except requests.ConnectionError:
        messages.warning(request,f"sales {s.id} can't be cancelled operational error")
        return render(request,'sales_orders/sales.html',{})
    

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
            shipment.status = ShipStatus(id=2)
            shipment.save()
            url = env('BASE_URL')+'/sales/ships/approve/'
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
@api_view(['POST'])
def sales_api(request):
    try:
        data = request.data
        id =  data['ref']
        status = data['status']
        draft = Shipment.objects.get(id=id)
        sale = draft.sales
        status = SalesStatus(id=status)
        if int(status.id) == PAYED:
            sale.status = status
            sale.save()
            n = Notifications.objects.create(title='Sales team Update',
            message=f'Sales order {data['ref']} status update: Payed by customer',link = reverse_lazy('get_sale',args=[sale.id]),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
            return Response({'data':'successfully updated'},status=201)
        else:
            n = Notifications.objects.create(title='Sales team Update Error',
            message=f'Sales order {data['ref']} Update error',link = reverse_lazy('get_sale',args=[sale.id]),
            tag='danger')
            n.user.add(User.objects.get(user_type=3))
            return Response({'error':'invalid status'},status=403)
    except Shipment.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
            




@login_not_required
@api_view(["POST"])
def package_api(request):
    try:
        data =  request.data
        package = Package.objects.get(id=data['ref'])
        sales = package.sales
        package.status = PackageStatus(PACKAGE_PACKED)
        sales.status = SalesStatus(SALE_PACKED)
        package.save()
        sales.save()
        n = Notifications.objects.create(title='Sales team Update',
        message=f'Package {data['ref']} status update: Item packed',link = reverse_lazy('get_package',args=[data['ref']]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except Package.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)

@login_not_required
@api_view(["POST"])
def ship_api(request):
    try:
        data = request.data
        draft = Shipment.objects.get(id=data['ref'])
        status = ShipStatus(id=data['status'])
        package = draft.package.all()
        sales = draft.sales
        draft.status = status
        st = ''
        if int(status.id) == CARRIER_PICKED:
            sales.status = SalesStatus(SALE_SHIPPED)
            package.update(status=PackageStatus(PACKAGE_SHIPPED))
            st = 'Order picked by carrier'
        elif int(status.id) == CUSTOMER_RECEIVED:
            sales.status = SalesStatus(SALE_DELIVERED)
            st = 'Order received by customer'
        else:
            n = Notifications.objects.create(title='Sales team Update Error',
            message=f'Ship order {data['ref']} update error ',link = reverse_lazy('get_ship',args=[data['ref']]),
            tag='danger')
            n.user.add(User.objects.get(user_type=3))
            return Response({'data':'cant be updated'},status=403)
        draft.save()
        sales.save()
        n = Notifications.objects.create(title='Sales team Update',
        message=f'Ship order {data['ref']} status update: {st}',link = reverse_lazy('get_ship',args=[data['ref']]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except Shipment.DoesNotExist:
            return HttpResponse({'error':'order does not exist'},status=404)
    except ShipStatus.DoesNotExist:
            return HttpResponse({f'error':'invalid data: status:{status}'},status=404)