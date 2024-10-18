from django.template.response import TemplateResponse as render
from django.shortcuts import redirect,HttpResponseRedirect,HttpResponse
from purchase_orders.models import PurchaseOrder,ReceiveStatus,PurchaseDraft,PurchaseReceive,PurchaseStatus,PurchaseItems,PurchasesItems
from inventory.models import Inventory,ShipMethod
from warehouse.models import Warehouse
from supplier.models import Supplier
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from accounts.models import User
import requests
from core.utils import specialilst_check,user_passes_test,date_filter
from purchase_orders.serializers import PurchasesSerializer
from django.contrib import messages
from core.models import Notifications
from django.urls import reverse_lazy
import environ
from django.contrib.auth.decorators import login_not_required
from django.db import IntegrityError

env = environ.Env()
environ.Env.read_env()



DRAFT = 1
PURCHASE_APPROVE = 2
SUPPLIER_APPROVE = 3
ORDER_PROCESSED = 4
SHIPPED = 5
DISPATCHED = 6
RECIEVE_DRAFT = 1
IN_TRANSIT = 2
PAYED = 3




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
def view_purchases(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    purchases = PurchaseOrder.objects.filter(warehouse=request.w).order_by(orderby)
    date_filter(date,purchases)
    return render(request,'purchases.html',{'purchases':purchases})

def view_recieved(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    recieved = PurchaseReceive.objects.filter(ref__order__warehouse=request.w).order_by(orderby)
    date_filter(date,recieved)
    return render(request,'recieved.html',{'recieved':recieved})

def get_purchase(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        purchase = PurchaseOrder.objects.get(id=draft)
        return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase})
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
        

# making purchase from inventory
# @user_passes_test(specialilst_check)
# def make_purchase(request):
#     if request.method == 'GET':
#         id_list =  request.GET.getlist('item') 
#         items = Inventory.objects.filter(id__in=id_list)
#         if len(items)>=1:
#             purchase_list = []
#             purchase = PurchaseDraft.objects.create()
#             for i in items:
#                 purchase_list.append(PurchasesItems(
#                     purchase = purchase,
#                     item = i,
#                     price = i.selling_price,
#                     quantity = 1,
#                     units = i.units
#                 ))
#             draft = PurchaseItems.objects.bulk_create(purchase_list)
#             return redirect(draft_purchase,id=purchase.id,permanent=True)
#         else:
#             return redirect('inventories')
#     else:
#         return render(request,'404.html',{})
    
@user_passes_test(specialilst_check)
def make_purchase(request,id):
    try:
        if request.method == 'GET':
            i = Inventory.objects.get(id=id)
            purchase = PurchaseDraft.objects.create()
            PurchaseItems.objects.create(purchase = purchase,
                    item = i,
                    price = i.selling_price,
                    quantity = i.reorder_point,
                    units = i.units)
            return redirect(draft_purchase,id=purchase.id)
        else:
            return redirect('inventories')
    except Inventory.DoesNotExist:
        return render(request,'404.html',{},status=404)
        

@user_passes_test(specialilst_check)
def draft_purchase(request,id):
    try:
        purchase = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=id)
        order = PurchaseOrder.objects.filter(id=purchase) 
        if request.method == 'POST':
            if not items or (order and (order.first().cancel or order.first().status.id>=DISPATCHED)):
                return HttpResponseRedirect(request.path_info)
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            for i in range(len(item)):
                sale = PurchaseItems.objects.get(id=item[i])
                sale.quantity = quantity[i]
                if int(quantity[i]) > 0:
                    sale.save()
            return HttpResponseRedirect(request.path_info)
        suppliers = Supplier.objects.all()
        if not items or (order and (order.first().cancel or order.first().status.id>=DISPATCHED)):
            return render(request,'404.html',{},status=404)
        ship_method = ShipMethod.objects.all()
        supplier = ''
        s = request.GET.get('supplier')
        if s:
            supplier = Supplier.objects.get(id=s)
        elif items.first().item.preferred_supplier:
            supplier = items.first().item.preferred_supplier
        else:
            supplier = suppliers.first()
        purchase.supplier = supplier
        purchase.save()
        return render(request,'purchase.html',{'number':id,'items':items,'suppliers':suppliers,'ship_method':ship_method,'supplier':supplier,'date':datetime.today()})
    except KeyError:
        return render(request,'404.html',{})
    except PurchaseDraft.DoesNotExist:
        return render(request, '404.html',{},status=404)
    

def purchase(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = draft.items.all()
        purchase = PurchaseOrder.objects.filter(id=draft)
        if specialilst_check and request.method == 'POST':
            total = 0
            for i in items:
                total += i.total_price
            supplier = draft.supplier
            bill = request.POST['bill_address']
            ship = request.POST['ship_address']
            sh= request.POST.get('ship_method')
            ship_method = ShipMethod.objects.get(id=sh)
            p_date = request.POST['preferred_date']
            p_date = datetime.strptime(p_date,'%m/%d/%Y, %I:%M:%S %p')
            status = PurchaseStatus.objects.get(status='draft')
            if not purchase:
                purchase = PurchaseOrder.objects.create(id=draft,created_date=datetime.now() ,warehouse=Warehouse.objects.get(id=request.w),bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=total)
                return redirect('get_purchase',id=draft.id)
            if purchase.first().cancel:
                return render(request,'404.html',status=400)
            purchase.update(bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,total_amount=total)
            if purchase[0].status.id >= PURCHASE_APPROVE:
                purchase_approve(request=request,id=id)
            if purchase[0].status.id  > PURCHASE_APPROVE:
                supplier_approve(request=request,id=id)
            return redirect('get_purchase',id=id)
        elif purchase :
            return redirect('get_purchase',id=draft.id)
        else:
            return render(request,'404.html',{},status=404)
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except ShipMethod.DoesNotExist:
        return HttpResponseRedirect(request.path_info,status=400)
    # except KeyError:
    #     return HttpResponseRedirect(request.path_info,status=400)
    # except ValueError:
    #     return HttpResponseRedirect(request.path_info,status=400)
   
@user_passes_test(specialilst_check) 
def cancel_purchase(request, id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        purch = draft.order
        supplier = draft.supplier.id
        id_val = purch.status.id
        recieve = PurchaseReceive.objects.filter(ref=draft)
        if recieve and recieve.first().status.id >= IN_TRANSIT:
            messages.add_message(request,messages.ERROR,'Cant cancel the order')
            return redirect('get_purchase',id=id)
        if id_val == DRAFT:
            draft.delete()
            return redirect('purchases')
        elif id_val == PURCHASE_APPROVE:
            warehouse = request.w
            url = env('BASE_URL')+f'/{warehouse}/purchases/cancel/'
            requests.post(url,json={'ref':id})
        elif id_val > PURCHASE_APPROVE:
            url = env('BASE_URL')+f'/supplier/{supplier}/cancel/'
            requests.post(url,json={'ref':id,'warehouse':request.w})
            if recieve:
                recieve.first().recieve.cancel = True    
                recieve.save()
        purch.cancel = True
        purch.save()
        return redirect('get_purchase',id=id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect('get_purchase',id=id)
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseOrder.DoesNotExist:
        return render(request,'404.html',{},status=404)
        
    
    
@user_passes_test(specialilst_check)
def approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        purch = PurchaseOrder.objects.get(id=draft) 
        if purch.status.id == DRAFT:
            return redirect(purchase_approve,id=id)
        elif purch.status.id  == PURCHASE_APPROVE:
            return redirect(supplier_approve, id=id)
        else:
            return render(request,'404.html',{},status=400)
    except PurchaseDraft.DoesNotExist:
            return render(request,'404.html',{},status=404)
    except PurchaseOrder.DoesNotExist:
            return render(request,'404.html',{},status=404)
        

@user_passes_test(specialilst_check)
def purchase_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = draft.items.all()
        purch = draft.order
        if purch.status.id >= SUPPLIER_APPROVE:
            return redirect(get_purchase,id=id)
        if purch.cancel:
            messages.add_message(request,messages.WARNING,'already cancelled')
            return redirect(get_purchase,id=id)
        data = {'ref':id,
                'items':items,
                'order':draft,
                'purchase':purch}
        serializer = PurchasesSerializer(data)
        # json = JSONRenderer().render(serializer.data)
        warehouse = request.w
        url = env('BASE_URL')+f'/{warehouse}/purchases/approve/'
        response = requests.post(url,json=serializer.data)
        if response.status_code == 201:
            purch.save()
            messages.add_message(request,messages.SUCCESS,'Data sent for approve')
        else:
            messages.add_message(request,messages.ERROR,'Invalid data or format')
        return redirect('get_purchase',id=id)
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseOrder.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseItems.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(get_purchase,id)
    
    
@user_passes_test(specialilst_check)
def supplier_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        supplier = draft.supplier.id
        items = draft.items.all()
        status = PurchaseStatus.objects.get(id=3)
        purch = draft.order
        if purch.cancel or purch.status.id > SHIPPED or purch.status.id < PURCHASE_APPROVE:
            messages.add_message(request,messages.WARNING,'cancelled order or data not valid at the moment')
            return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purch},status=401)
        data = {'ref':id,
                'items':items,
                'order':draft,
                'purchase':purch}
        serializer = PurchasesSerializer(data)
        purchase.status = status
        url = env('BASE_URL')+f'/supplier/{supplier}/approve/'
        response = requests.post(url,json=serializer.data)
        if response.status_code == 201:
            purch.save()
            messages.add_message(request,messages.SUCCESS,'Data sent for approve')
        else:
            messages.add_message(request,messages.ERROR,'Data not accepted')
        return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purch})
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseOrder.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseItems.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(get_purchase,id)
    
@login_not_required
@api_view(['POST'])
def purchase_api(request):
    try:
        data = request.data
        ref = data['ref']
        draft = PurchaseDraft.objects.get(id=ref)
        status = PurchaseStatus.objects.get(id=2)
        purchase = PurchaseOrder.objects.get(id=draft)
        if purchase.status.id != DRAFT:
            return Response({'error':'invalid operation'},status=400)
        purchase.status = status
        purchase.save()
        n = Notifications.objects.create(title='Purchase Approval',
        message=f'Purchase order {ref} approved by Purchase team',link = reverse_lazy('purchase',args=[ref]),tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PurchaseOrder.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except KeyError:
            return Response({'error':'Invalid request'},status=400)
        
@login_not_required
@api_view(['POST'])
def supplier_api(request):
    try:
        data = request.data
        ref = data['ref']
        status = data['status']
        draft = PurchaseDraft.objects.get(id=ref)
        status = PurchaseStatus.objects.get(id=status)
        purchase = PurchaseOrder.objects.get(id=draft)
        if purchase.cancel:
            return Response({'error':'order is already cancelled'},status=401)
        if int(status.id) == DISPATCHED:
            items = PurchaseItems.objects.filter(purchase=draft)
            for i in items:
                i.item.on_hand += i.quantity
                i.item.save()
        purchase.status = status
        purchase.save()
        n = Notifications.objects.create(title=f'Supplier Update: {status.status.title()}',
        message=f'Purchase order {ref} status update: {status.status}',link = reverse_lazy('purchase',args=[ref]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PurchaseOrder.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PurchaseStatus.DoesNotExist:
        return Response({'error':'invalid status value'},status=400)
    except KeyError:
        return Response({'error':'Invalid request'},status=400)
    
@login_not_required
@api_view(['POST'])
def recieve_api(request):
    try:
        data = request.data
        ref = data['ref']
        status = data['status']
        draft = PurchaseDraft.objects.get(id=ref)
        if draft.order.status.id != DISPATCHED or draft.order.cancel:
            return Response({'error':'order is either cancelled or not dispached yet'},status=401)
        status = ReceiveStatus.objects.get(id=status)
        if status.id == RECIEVE_DRAFT:
            PurchaseReceive.objects.create(status=status,ref=draft)
        elif status.id == IN_TRANSIT:
            delivered = datetime.now()
            p = PurchaseReceive.objects.get(ref=draft)
            p.delivered_date = delivered
            p.status = status
            p.save()    
        elif status.id == PAYED:
            p = PurchaseReceive.objects.get(ref=draft)
            p.status = status
            p.save()         
        n = Notifications.objects.create(title=f'Supplier Update {status.status.title()}',
        message=f'Purchase order {ref} status update: {status.status}',link = reverse_lazy('recieved'),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PurchaseOrder.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except PurchaseReceive.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except ReceiveStatus.DoesNotExist:
        return Response({'error':'invalid status value'},status=400)
    except IntegrityError:
        return Response({'data':'Already updated'},status=200)
    except KeyError:
        return Response({'error':'Invalid request'},status=400)