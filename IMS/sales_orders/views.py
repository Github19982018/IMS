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
environ.Env.read_env()
from sales_orders.serializer import PackSerializer,ShipSerializer
import environ

env = environ.Env()
environ.Env.read_env()

# Create your views here.
def view_sales(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    sales = Sales.objects.filter(warehouse=request.w).order_by(orderby)
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        sales = sales.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        sales = sales.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        sales = sales.filter(updated__year=year)
    return render(request,'sales_orders/sales.html',{'sales':sales})

def view_packages(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    packages = Package.objects.filter(sales__warehouse=request.w).order_by(orderby)
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        packages = packages.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        packages = packages.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        packages = packages.filter(updated__year=year)
    return render(request,'sales_orders/packages.html',{'packages':packages})

def view_ships(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    ships = Shipment.objects.filter(sales__warehouse=request.w).order_by(orderby)
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        ships = ships.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        ships = ships.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        ships = ships.filter(updated__year=year)
    return render(request,'sales_orders/ships.html',{'ships':ships})

def get_sales(request,id):
    try:
        Sales.objects.get(id=id)
        return redirect(sales,id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})

# making Sales from inventory
# @user_passes_test(specialilst_check)
# def make_sales(request):
#     if request.method == 'POST':
#         id_list =  request.POST.getlist('item') 
#         if len(id_list)>=1:
#             items = Inventory.objects.filter(id__in=id_list)
#             w = request.w
#             warehouse = Warehouse.objects.get(id=w)
#             # warehouse = Warehouse.objects.all()
#             sales = Sales.objects.create(warehouse=warehouse)
#             sales_list = []
#             for i in items:
#                 sales_list.append(SaleItems(
#                     sales = sales,
#                     item = i,
#                     price = i.selling_price,
#                     quantity = 1,
#                     units = i.units
#                 ))
#             draft = SalesItems.objects.bulk_create(sales_list)
#             return redirect(draft_sales,request=request,id=sales.id)
#     messages.add_message(request,messages.WARNING,'please select an item to order')    
#     return redirect('inventories')


def get_package(request,id):
    try:      
        pack = Package.objects.get(id=id)
        if pack.status == 'draft':
            return redirect(package_draft,id=id)
        else:
            return redirect(package,id=id)
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
        if len(id_list)>=1:
            items = Inventory.objects.filter(id__in=id_list)
            customer = customers.first()
            return render(request,'sales_orders/sales_draft.html',{'items':items,'customer':customer,'customers':customers,'ship_method':ship_method,'date':datetime.today()})
        else:
            messages.add_message(request,messages.WARNING,'please select an item to order')    
            return redirect('inventories')
        
    # else:
    #     s = request.GET.get('customer')
    #     customer = ''
    #     if s:
    #         try:
    #             customer = Customer.objects.get(id=s)
    #         except Customer.DoesNotExist:
    #             customer = Customer.objects.first()
    #     else:
    #         customer = Customer.objects.first()
    #     sales.customer = customer
    #     sales.save()
    #     return render(request,'sales_orders/sale_draft.html',{'number':id,'items':draft,'customers':customers,'ship_method':ship_method,'customer':customer,'date':datetime.today()})


@user_passes_test(specialilst_check)
def save_quantity(request):
    try:
        if request.method == 'POST':
            warehouse = Warehouse.objects.get(id=request.w)
            sale = Sales.objects.create(warehouse=warehouse,customer=Customer.objects.first())
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            sales_list = []
            items = Inventory.objects.filter(id__in=item)
            for i in range(len(items)):
                sales_list.append(SaleItems(
                    sales = sale,
                    item = items[i],
                    price = items[i].selling_price,
                    quantity = quantity[i],
                    units = items[i].units
                ))
            draft = SalesItems.objects.bulk_create(sales_list)
            return redirect(sales,id=sale.id,permanent=True)
        else:
            sale = Sales.objects.get(id=id)
            return redirect(sales,id=sale.id,permanent=True)
    except Customer.DoesNotExist:
        pass
    except Sales.DoesNotExist:
        return render(request,'404.html',{})


        
# @user_passes_test(specialilst_check)
def sales(request,id):
    try: 
        sales = Sales.objects.get(id=id)
        draft = SalesItems.objects.filter(sales=sales)
        if request.method == 'GET':
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
        elif request.method == 'POST' and specialilst_check:
            sales.bill_address = request.POST['bill_address']
            sales.ship_address = request.POST['ship_address']
            customer = request.POST['customer']
            sales.customer = Customer.objects.get(id=customer)
            # sales.total_price = request.POST['total_price']
            sh= request.POST['ship_method'] or 1
            sales.ship_method = ShipMethod.objects.get(id=sh)
            p_date = request.POST['preferred_date']
            sales.preferred_shipping_date = datetime.strptime(p_date,'%m/%d/%Y, %I:%M:%S %p')
            sales.status = SalesStatus.objects.get(status='draft')
            sales.warehouse = Warehouse.objects.get(id=request.w)
            sales.save()
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})
    except SalesItems.DoesNotExist:
        return  render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def edit_sales(request,id):
    try:
        ship_method = ShipMethod.objects.all()
        customers = Customer.objects.all()
        sale = Sales.objects.get(id=id)
        items = SalesItems.objects.filter(sales=sale)
        return render(request,'sales_orders/sales_edit.html',{'items':items,'sales':sale,'ship_method':ship_method, 'customers':customers})
    except Sales.DoesNotExist:
        return render(request,'404.html',{})

@user_passes_test(specialilst_check)
def package_draft(request,id):
    try:
        sales = Sales.objects.get(id=id)
        ship_method = ShipMethod.objects.all()
        customers = Customer.objects.all()
        items = SalesItems.objects.filter(sales=sales)
        p = Package.objects.get(sales=sales)
        return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p,'ship_method':ship_method,'customers':customers})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{})
    except Package.DoesNotExist:
        p = Package.objects.create(sales=sales,created_at=datetime.now(),status=PackageStatus(id=1),customer=sales.customer,shipping_address=sales.ship_address)
        return render(request,'sales_orders/package_draft.html',{'number':p.id,'items':items, 'sales':sales, 'package' :p,'ship_method':ship_method,'customers':customers})

@user_passes_test(specialilst_check)
def package(request,id):
    try:
        package = Package.objects.get(id=id)
        package.status = PackageStatus(id=1)
        package_approve(request,id)
        package.save()
        sales = package.sales
        items = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/package.html',{'package':package,'items':items, 'sales':sales})
    except Package.DoesNotExist:
        return render(request,'404.html',{})  
  
@user_passes_test(specialilst_check)  
def delete_package(request,id):
    try:
        package = Package.objects.get(id=id)
        if package.status.id <= 3:
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
        sales = Sales.objects.get(id=id)
        shiplist = Shipment.objects.filter(sales=sales)
        if request.method == 'POST' and specialilst_check:
            if shiplist:
                [sh,] = shiplist
            else:            
                import random
                track=random.randint(100000000000,9999999999999)
                sh = Shipment.objects.create(sales=sales,tracking_number=track,ship_method=sales.ship_method,customer=sales.customer,shipment_address=sales.ship_address)
            # ship.sales.add(sales)
            pack = request.POST.getlist('package')
            packages = Package.objects.filter(id__in=pack)
            packages.update(ship=sh)
            items = sales.items.all()
            return render(request,'sales_orders/ship.html',{'number':id, 'sales':sales,'ship':sh, 'packages':packages, 'items':items})
        # items = sales.items
        else:
            if shiplist:
                [sh,] = shiplist
                packages = sh.package.all()
                items = sales.items.all()
                return render(request,'sales_orders/ship.html',{'number':id, 'sales':sales,'ship':sh, 'packages':packages, 'items':items})
    except Sales.DoesNotExist:
        return render(request,'404.html',{})

@user_passes_test(specialilst_check)
def cancel_ship(request,id):
    try:
        sh = Shipment.objects.get(id=id)
        if sh.status.id < 4:
            sh.status = ShipStatus.objects.get(status='cancelled')
            sh.save()
            messages.info(request,f"shipment {sh.id} cancelled")
            return redirect('ships')
        else:
            messages.warning(request,f"shipment {sh.id} cant be cancelled already received")
            return redirect('get_ship',id=id)
    except Shipment.DoesNotExist:
        return render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def cancel_sales(request,id):
    try:
        s = Sales.objects.get(id=id)
        if s.status.id < 5:
            s.status = SalesStatus.objects.get(status='cancelled')
            try:
                s.package.all().delete()
                s.shipment.all().update(status=ShipStatus(status='cancelled'))
            except:
                pass
            s.save()
            messages.info(request,f"sales {s.id} cancelled")
            return redirect('sales')
        else:
            messages.warning(request,f"sales {s.id} cant be cancelled already shiped")
            return redirect('get_sales',id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    

@user_passes_test(specialilst_check)
def create_ship(request,id):
    try:
        sales = Sales.objects.get(id=id)
        shipment = Shipment.objects.get(sales=sales)
        packages = shipment.package.all()
        items = sales.items.all()
        data = {'ref':id,
                'shipment':shipment,
                'packages':packages,
                'items':items}
        shipment.status = ShipStatus(id=2)
        shipment.save()
        url = env('BASE_URL')+'/sales/ships/approve'
        data = ShipSerializer(data)
        try:
            requests.post(url,data)
            messages.add_message(request,messages.SUCCESS,'Successfully send for approval')
        except requests.exceptions.ConnectionError:
            messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(ship,id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    except Shipment.DoesNotExist:
        return HttpResponseRedirect('')


def package_approve(request,id):
    try:
        status = PackageStatus(id=4)
        packages = Package.objects.get(id=id)
        items = SalesItems.objects.get(sales=sales)
        packages.status = status
        data = {
            'ref':id,
            'items':items,
            'packages': packages
        }
        url = env('BASE_URL')+'/sales/packages/approve'
        data = PackSerializer(data)
        print(data.data)
        try:
            requests.post(url,data)
            packages.save()
        except requests.exceptions.ConnectionError:
            messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return
    except Sales.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
        return 
    except SalesItems.DoesNotExist:
        messages.add_message(request,messages.ERROR,'Invalid data input')
        return


@api_view(['POST'])
def sales_api(request):
    try:
        data = request.data
        id =  data['ref']
        status = data['status']
        draft = Sales.objects.get(id=id)
        status = SalesStatus(id=status)
        draft.status = status
        draft.save()
        return Response({'data':'successfully updated'},status=201)

    except Sales.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)




@api_view(["POST"])
def package_api(request):
    try:
        data =  request.data
        package = Package.objects.get(id=data['ref'])
        sales = package.sales
        package.status = PackageStatus(2)
        sales.status = SalesStatus(3)
        package.save()
        sales.save()
        return Response({'data':'successfully updated'},status=201)
    except KeyError:
            return Response({'error':'Invalid data'},status=404)
    except Package.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)

@api_view(["POST"])
def ship_api(request):
    try:
        data = request.data
        draft = Shipment.objects.get(id=data.ref)
        status = ShipStatus(id=status)
        sales = draft.sales
        draft.status = status
        if status == 2:
            sales.status = 3
        elif status == 3:
            sales.status = 4
        draft.save()
        sales.save()
        return Response({'data':'successfully updated'},status=201)
    except KeyError:
            return Response({'error':'Invalid data'},status=404)
    except Shipment.DoesNotExist:
            return HttpResponse({'error':'order does not exist'},status=404)
    except ShipStatus.DoesNotExist:
            return HttpResponse({f'error':'invalid data: status:{status}'},status=404)