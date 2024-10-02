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
        return render(request,'404.html',{})


@user_passes_test(specialilst_check)
def draft_sales(request):
    if request.method == 'POST':
        id_list =  request.POST.getlist('item') 
        if id_list:
            ship_method = ShipMethod.objects.all()
            customers = Customer.objects.all()
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
            sale.status = SalesStatus.objects.get(status='draft')
            sale.total_amount = total
            sale.save()
            draft = SalesItems.objects.bulk_create(sales_list)
            return sales(request,sale.id)
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
            if not sales.status:
                sales.status = SalesStatus.objects.get(status='draft')
            sales.warehouse = Warehouse.objects.get(id=request.w)
            sales.save()
            print(sales.ship_method)
            return render(request,'sales_orders/sale.html',{'number':id,'items':draft, 'sales':sales})
        else: 
            sales = Sales.objects.get(id=id)
            draft = SalesItems.objects.filter(sales=sales)
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
            if request.method == 'POST':
                return redirect(sales,id=id)
            else:
                ship_method = ShipMethod.objects.all()
                customers = Customer.objects.all()
                items = SalesItems.objects.filter(sales=sale)
                return render(request,'sales_orders/sales_edit.html',{'items':items,'sales':sale,'ship_method':ship_method, 'customers':customers})
        else:
            return render(request,'404.html',{})
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    

    
@user_passes_test(specialilst_check)
def cancel_sales(request,id):
    try:
        s = Sales.objects.get(id=id)
        if not s.status or s.status.id == SALE_DRAFT:
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
                items = s.items.all()
                for i in items:
                    i.item.on_hand += i.quantity
                    i.item.save()
                messages.info(request,f"sales {s.id} cancelled")
            return redirect('sales')
        else:
            messages.warning(request,f"sales {s.id} cant be cancelled")
            return redirect('get_sale',id=id)
    except Sales.DoesNotExist:
        return render(request,'404.html',{})
    except requests.ConnectionError:
        messages.warning(request,f"sales {s.id} can't be cancelled operational error")
        return render(request,'sales_orders/sales.html',{})
    


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
            


