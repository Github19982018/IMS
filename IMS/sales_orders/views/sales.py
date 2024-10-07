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
    week = datetime.now().isocalendar()[1]
    if date=='today':
        queryset = queryset.filter(updated__day=day)
    if date == 'month':
        queryset = queryset.filter(updated__month=month)
    elif date == 'year':
        queryset = queryset.filter(updated__year=year)
    elif date == 'week':
        queryset = queryset.filter(updated__week=week)
    return queryset

# Create your views here.
def view_sales(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    sales = Sales.objects.filter(warehouse=request.w).order_by(orderby)
    sales = date_filter(date, sales)
    return render(request,'sales_orders/sales.html',{'sales':sales})

def get_sales(request,id):
    try:
        sales = Sales.objects.get(id=id)
        draft = SalesItems.objects.filter(sales=sales)
        return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    except Sales.DoesNotExist:
        return render(request,'404.html',{},status=404)


@user_passes_test(specialilst_check)
def draft_sales(request):
    if request.method == 'POST':
        id_list =  request.POST.getlist('item') 
        items = Inventory.objects.filter(id__in=id_list)
        if items:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            customer = customers.first()
            return render(request,'sales_orders/sales_draft.html',{'items':items,'customer':customer,'customers':customers,'ship_method':ship_method,'date':datetime.today()})
        else:
            messages.add_message(request,messages.WARNING,'please select a valid item to order')    
            return redirect('inventories')
    else:
        return render(request,'404.html',status=405)
    
def create_sales_items(sale,items,quantity):
    sales_list = []
    total = 0
    for i in range(len(items)):
        sales_list.append(SaleItems(
            sales = sale,
            item = items[i],
            price = items[i].selling_price,
            quantity = quantity[i],
            units = items[i].units
        ))
        if 0 > quantity[i] > items[i].on_hand:
            raise(ValueError)
        total += float(quantity[i])*float(items[i].selling_price)
    return sales_list,total


@user_passes_test(specialilst_check)
def save_items(request):
    try:
        if request.method != 'POST':
            return render(request,'404.html',status=405)
        warehouse = Warehouse.objects.get(id=request.w)
        quantity = request.POST.getlist('quantity')
        item = request.POST.getlist('item')
        items = Inventory.objects.filter(id__in=item)
        if not items:
            return render(request,'404.html',status=404)   
        sale = Sales.objects.create(warehouse=warehouse,customer=Customer.objects.first(),status=SalesStatus.objects.get(id=1))
        sales_list,total = create_sales_items(sale,items,quantity)
        sale.status = SalesStatus.objects.get(status='draft')
        sale.total_amount = total
        draft = SalesItems.objects.bulk_create(sales_list)
        sale.save()
        # return sales(request,sale.id)
        return sales(request=request,id=sale.id)
    except ValueError:
        messages.add_message(request,messages.WARNING,'invalid value')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


        
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
            if not sales.status:
                sales.status = SalesStatus.objects.get(status='draft')
            sales.warehouse = Warehouse.objects.get(id=request.w)
            sales.save()
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
        else: 
            sales = Sales.objects.get(id=id)
            draft = SalesItems.objects.filter(sales=sales)
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
    except Sales.DoesNotExist:
        return  render(request,'404.html',{},status=404)
    except Customer.DoesNotExist:
        return HttpResponseRedirect(request.path_info)
    except ShipMethod.DoesNotExist:
        return  HttpResponseRedirect(request.path_info)
    
@user_passes_test(specialilst_check)
def edit_sales(request,id):
    try:
        sale = Sales.objects.get(id=id)
        if sale.status.id >= 5:
            return render(request,'404.html',{})
        if request.method == 'POST':
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            for i in range(len(item)):
                sale = SalesItems.objects.get(id=item[i])
                sale.quantity = quantity[i]
                sale.save()
            return sales(request,id)
        else:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
            items = SalesItems.objects.filter(sales=sale)
            return render(request,'sales_orders/sales_edit.html',{'items':items,'sales':sale,'ship_method':ship_method, 'customers':customers})
    except Sales.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except SalesItems.DoesNotExist:
        return render(request,'404.html',{},status=404)
    
import threading
@user_passes_test(specialilst_check)
def cancel_sales(request,id):
    try:
        sale = Sales.objects.get(id=id)
        packages = Package.objects.filter(sales=sale)
        if not packages:
            sale.delete()
            n = Notifications.objects.create(title='Sales team Update: Cancel Success',
            message=f'sales {id} deleted',link = reverse_lazy('sales'),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
            return redirect('sales')
        else:
            warehouse = request.w
            thread = threading.Thread(target=sales_cancel,args=[sale,warehouse])
            thread.start()
            messages.info(request,f"Sales order {id} is set for cancel will be updated on completion")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
    except Sales.DoesNotExist:
        messages.error(request,f"sales {id} can't be cancelled invalid order")
        return render(request,'404.html',{},status=404)

def cancel_error(id,message):
    n = Notifications.objects.create(title='Sales team Update: Cancel Error',
    message=f'sales {id} {message}',link = reverse_lazy('get_sale',args=[id]),
    tag='danger')
    n.user.add(User.objects.get(user_type=3))
    return

def cancel_packages(sale,warehouse):
    p = sale.package.all()
    url = env('BASE_URL')+f'{warehouse}/sales/packages/cancel/'
    res = requests.post(url,json={'ref':list(p.values_list('id',flat=True))})
    if res.status_code != 201:
        cancel_error(id,'cant be cancelled try again later')
        raise(AssertionError)
    p.delete()
    
def cancel_ships(sale,warehouse):
    sh = Shipment.objects.filter(sales=sale)
    if not sh:
        return
    url = env('BASE_URL')+ f'{warehouse}/sales/ships/cancel/'
    res = requests.post(url,json={'ref':[sh.id]})
    if res.status_code != 201:
        cancel_error(id,'cant be cancelled try again later')
        raise(AssertionError)
    sh.update(cancel=True)

@user_passes_test(specialilst_check)
def sales_cancel(sale,warehouse):
    try:
        if sale.status.id >= SALE_SHIPPED :
            return cancel_error(id,'cant be cancelled invalid order')   
        cancel_packages(sale,warehouse)
        cancel_ships(sale,warehouse)
        if sale.status > SALE_PACKED:
            items = sale.items.all()
            for i in items:
                i.item.on_hand += i.quantity
                i.item.save()
        sale.status = SalesStatus.objects.get(status='cancelled')
        sale.save()
        n = Notifications.objects.create(title='Sales team Update: Cancel Success',
        message=f'sales {id} cancelled',link = reverse_lazy('get_sale',args=[id]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
    except requests.ConnectionError:
        return cancel_error(id,'cant be cancelled connection error')
    except AssertionError:
        return 
    
    