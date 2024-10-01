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
from core.utils import specialilst_check,user_passes_test
from purchase_orders.serializers import PurchasesSerializer
from django.contrib import messages
from core.models import Notifications
from django.urls import reverse_lazy
import environ
from django.contrib.auth.decorators import login_not_required
from django.db import IntegrityError

env = environ.Env()
environ.Env.read_env()



# Create your views here.
def view_purchases(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    purchases = PurchaseOrder.objects.filter(warehouse=request.w).order_by(orderby)
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        purchases = purchases.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        purchases = purchases.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        purchases = purchases.filter(updated__year=year)
    return render(request,'purchases.html',{'purchases':purchases})

def view_recieved(request):
    date = request.GET.get('date','month')
    orderby = request.GET.get('orderby','id')
    recieved = PurchaseReceive.objects.filter(ref__order__warehouse=request.w).order_by(orderby)
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    if date=='today':
        recieved = recieved.filter(updated__day=day,updated__month=month,updated__year=year)
    if date == 'month':
        recieved = recieved.filter(updated__month=month,updated__year=year)
    elif date == 'year':
        recieved = recieved.filter(updated__year=year)
    return render(request,'recieved.html',{'recieved':recieved})

# def get_purchase(request,id):
#     draft = Purchase_items.objects.get(pk=id)
#     purchase = Purchase.objects.get(id=draft)
#     return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})

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
                    quantity = 1,
                    units = i.units)
            return redirect(draft_purchase,id=purchase.id)
        else:
            return redirect('inventories')
    except Inventory.DoesNotExist:
        return render(request,'404.html',{},status=404)
        

@user_passes_test(specialilst_check)
def draft_purchase(request,id):
    try:
        if request.method == 'POST':
            quantity = request.POST.getlist('quantity')
            item = request.POST.getlist('item')
            for i in range(len(item)):
                sale = PurchaseItems.objects.get(id=item[i])
                sale.quantity = quantity[i]
                sale.save()
            return HttpResponseRedirect(request.path_info)
        else:
            purchase = PurchaseDraft(id=id)
            draft = PurchaseItems.objects.filter(purchase=id)
            suppliers = Supplier.objects.all()
            if draft:
                ship_method = ShipMethod.objects.all()
                def set_supplier():
                    supplier = ''
                    s = request.GET.get('supplier')
                    if s:
                        supplier = Supplier.objects.get(id=s)
                    elif draft.first().item.preferred_supplier:
                        supplier = draft.first().item.preferred_supplier
                    else:
                        supplier = suppliers.first()
                    purchase.supplier = supplier
                    purchase.save()
                    return supplier
                supplier = set_supplier()
                return render(request,'purchase.html',{'number':id,'items':draft,'suppliers':suppliers,'ship_method':ship_method,'supplier':supplier,'date':datetime.today()})
            else:     
                return render(request,'404.html',{},status=404)
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
            if purchase:
                purchase.update(bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,total_amount=total)
                approve(request,id)
                return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase.first()},status=201)
            else:
                purchase = PurchaseOrder.objects.create(id=draft,created_date=datetime.now() ,warehouse=Warehouse.objects.get(id=request.w),bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=total)
                return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase},status=201)
        elif purchase:
            return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase.first()},status=200)
        else:
            return render(request,'404.html',{},status=404)
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except ShipMethod.DoesNotExist:
        return HttpResponseRedirect(request.path_info,status=400)
    except KeyError:
        return HttpResponseRedirect(request.path_info,status=400)
    except ValueError:
        return HttpResponseRedirect(request.path_info,status=400)
   
@user_passes_test(specialilst_check) 
def cancel_purchase(request, id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        purch = draft.order
        id_val = purch.status.id
        if id_val == 1:
            draft.delete()
            return redirect('purchases')
        elif id_val == 2:
            url = env('BASE_URL')+'/purchases/cancel/'
            requests.post(url,json={'ref':id})
        elif id_val > 2:
            url = env('BASE_URL')+'/supplier/cancel/'
            requests.post(url,json={'ref':id})
            if draft.recieve:
                draft.recieve.cancel = True
                draft.recieve.save()
        purch.cancel = True
        purch.save()
        return redirect('purchase',id=id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect('purchase',id=id)
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except PurchaseOrder.DoesNotExist:
        return render(request,'404.html',{},status=404)
    except AttributeError:
        messages.add_message(request,messages.WARNING,'Cant connect to the server')
        return redirect('purchase',id=id)
        
    
    
@user_passes_test(specialilst_check)
def approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        purch = PurchaseOrder.objects.get(id=draft) 
        if purch.status.id == 1:
            return redirect(purchase_approve,id=id)
        elif purch.status.id  == 2:
            return redirect(supplier_approve, id=id)
        else:
            return render(request,'404.html',{},status=400)
    except PurchaseDraft.DoesNotExist:
            return render(request,'404.html',{},status=404)
        

@user_passes_test(specialilst_check)
def purchase_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        status = PurchaseStatus(id=1)
        purch = PurchaseOrder.objects.get(id=draft)
        if not purch.cancel:
            data = {'ref':id,
                    'items':items,
                    'order':draft,
                    'purchase':purch}
            serializer = PurchasesSerializer(data)
            # json = JSONRenderer().render(serializer.data)
            purch.status = status
            url = env('BASE_URL')+'/purchases/approve/'
            if serializer.is_valid:
                response = requests.post(url,json=serializer.data)
                if response.status_code == 201:
                    purch.save()
                    messages.add_message(request,messages.SUCCESS,'Data sent for approve')
                else:
                    messages.add_message(request,messages.ERROR,'Invalid data or format')
        else:
            messages.add_message(request,messages.WARNING,'already cancelled order')
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{})
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
    return redirect(purchase,id)
    
    
@user_passes_test(specialilst_check)
def supplier_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        status = PurchaseStatus(id=3)
        purch = PurchaseOrder.objects.get(id=draft)
        if not purch.cancel:
            data = {'ref':id,
                    'items':items,
                    'order':draft,
                    'purchase':purch}
            serializer = PurchasesSerializer(data)
            purchase.status = status
            url = env('BASE_URL')+'/supplier/approve/'
            response = requests.post(url,json=serializer.data)
            if response.status_code == 201:
                purch.save()
                messages.add_message(request,messages.SUCCESS,'Data sent for approve')
            else:
                messages.add_message(request,messages.ERROR,'Invalid data or format')
            return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purch})
    except PurchaseDraft.DoesNotExist:
        return redirect(purchase,id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(purchase,id)
    
@login_not_required
@api_view(['POST'])
def purchase_api(request):
    try:
        data = request.data
        ref = data['ref']
        draft = PurchaseDraft.objects.get(id=ref)
        status = PurchaseStatus.objects.get(id=2)
        purchase = PurchaseOrder.objects.get(id=draft)
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
        if not purchase.cancel:
            if int(status.id) == 6:
                items = PurchaseItems.objects.filter(purchase=draft)
                for i in items:
                    i.item.on_hand += i.quantity
                    i.item.save()
            purchase.status = status
            purchase.save()
            n = Notifications.objects.create(title='Supplier Update',
            message=f'Purchase order {ref} status update: {status.status}',link = reverse_lazy('purchase',args=[ref]),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
            return Response({'data':'successfully updated'},status=201)
        else:
            return Response({'error':'order is already cancelled'},status=401)
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
        if draft.order.status.id == 6 and not draft.order.cancel:
            status = ReceiveStatus.objects.get(id=status)
            if status.id == 1:
                PurchaseReceive.objects.create(status=status,ref=draft)
            elif status.id == 2:
                delivered = datetime.now()
                p = PurchaseReceive.objects.get(ref=draft)
                p.delivered_date = delivered
                p.status = status
                p.save()    
            elif status.id == 3:
                p = PurchaseReceive.objects.get(ref=draft)
                p.status = status
                p.save()         
            n = Notifications.objects.create(title='Supplier Update',
            message=f'Purchase order {ref} status update: {status.status}',link = reverse_lazy('recieved'),
            tag='success')
            n.user.add(User.objects.get(user_type=3))
            return Response({'data':'successfully updated'},status=201)
        else:
            return Response({'error':'order is either cancelled or not dispached yet'},status=401)
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