from django.template.response import TemplateResponse as render
from django.shortcuts import redirect,HttpResponseRedirect,HttpResponse
from purchase_orders.models import PurchaseOrder,PurchaseDraft,PurchaseReceive,Purchase_status,PurchaseItems,PurchasesItems
from inventory.models import Inventory,ShipMethod
from warehouse.models import Warehouse
from supplier.models import Supplier
from datetime import datetime, date
from rest_framework.decorators import api_view
from rest_framework.response import Response
from accounts.models import User
import requests
from core.utils import specialilst_check,user_passes_test
from purchase_orders.serializers import PurchasesSerializer
from django.contrib import messages
from core.models import Notifications
from django.urls import reverse_lazy



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

# def get_purchase(request,id):
#     draft = Purchase_items.objects.get(pk=id)
#     purchase = Purchase.objects.get(id=draft)
#     return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purchase})

# making purchase from inventory
@user_passes_test(specialilst_check)
def make_purchase(request):
    if request.method == 'GET':
        id_list =  request.GET.getlist('item') 
        items = Inventory.objects.filter(id__in=id_list)
        if len(items)>=1:
            purchase_list = []
            purchase = PurchaseDraft.objects.create()
            for i in items:
                purchase_list.append(PurchasesItems(
                    purchase = purchase,
                    item = i,
                    price = i.selling_price,
                    quantity = 1,
                    units = i.units
                ))
            draft = PurchaseItems.objects.bulk_create(purchase_list)
            return redirect(draft_purchase,id=purchase.id,permanent=True)
        else:
            return redirect('inventories')
    else:
        return render(request,'404.html',{})
    
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
            return redirect(draft_purchase,id=purchase.id,permanent=True)
        else:
            return redirect('inventories')
    except Inventory.DoesNotExist:
        return render(request,'404.html',{})
        

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
            ship_method = ShipMethod.objects.all()
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
            return render(request,'purchase.html',{'number':id,'items':draft,'suppliers':suppliers,'ship_method':ship_method,'supplier':supplier,'date':datetime.today()})
    except KeyError:
        return render(request,'404.html',{})
    except PurchaseDraft.DoesNotExist:
        return render(request, '404.html',{})

def purchase(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        purchase = PurchaseOrder.objects.filter(id=draft)
        if purchase:
            return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase.first()})
        elif specialilst_check and request.method == 'POST':
            total = 0
            for i in items:
                total += i.total_price
            supplier = draft.supplier
            bill = request.POST['bill_address']
            ship = request.POST['ship_address']
            sh= request.POST['ship_method']
            ship_method = ShipMethod.objects.get(id=sh)
            p_date = request.POST['preferred_date']
            p_date = datetime.strptime(p_date,'%m/%d/%Y, %I:%M:%S %p')
            status = Purchase_status.objects.get(status='draft')
            purchase = PurchaseOrder.objects.create(id=draft,warehouse=Warehouse.objects.get(id=request.w),bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=total)
            return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase})
        else:
            return render(request,'404.html',{})
    except PurchaseDraft.DoesNotExist:
        return render(request,'404.html',{})
    except KeyError:
        return HttpResponseRedirect(request.path_info)
   
@user_passes_test(specialilst_check) 
def cancel_purchase(request, id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        purch = PurchaseOrder.objects.get(id=draft)
        status = Purchase_status(status='cancel')
        purch.status = status
        items = PurchaseItems.objects.filter(purchase=draft)
        data = {'items':items,
                'order':draft,
                'purchase':purch}
        serializer = PurchasesSerializer(data)
        url = 'http://localhost:8081/purchases/update'
        requests.post(url,serializer.data,timeout=1)
        return redirect('purchase',id=id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect('purchase',id=id)

@user_passes_test(specialilst_check)
def purchase_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        status = Purchase_status(id=2)
        purch = PurchaseOrder.objects.get(id=draft)
        data = {'items':items,
                'order':draft,
                'purchase':purch}
        serializer = PurchasesSerializer(data)
        purchase.status = status
        url = 'http://localhost:8081/purchases/approve'
        requests.post(url,serializer.data)
        purch.save()
        return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purch})
    except PurchaseDraft.DoesNotExist:
        return redirect(purchase,id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(purchase,id)
    
    
@user_passes_test(specialilst_check)
def supplier_approve(request,id):
    try:
        draft = PurchaseDraft.objects.get(id=id)
        items = PurchaseItems.objects.filter(purchase=draft)
        status = Purchase_status(id=3)
        purch = PurchaseOrder.objects.get(id=draft)
        data = {'items':items,
                'order':draft,
                'purchase':purch}
        serializer = PurchasesSerializer(data)
        purchase.status = status
        url = 'http://localhost:8081/suppliers/approve'
        requests.post(url,serializer.data)
        purch.save()
        return render(request,'purchase_next.html',{'number':id,'items':[draft], 'purchase':purch})
    except PurchaseDraft.DoesNotExist:
        return redirect(purchase,id)
    except requests.exceptions.ConnectionError:
        messages.add_message(request,messages.ERROR,'Cant connect to the server')
        return redirect(purchase,id)

@api_view(['POST'])
def purchase_api(request):
    try:
        data = request.data
        ref = data['ref']
        draft = PurchaseDraft.objects.get(id=ref)
        status = Purchase_status(id=3)
        purchase = PurchaseOrder.objects.get(id=draft)
        purchase.status = status
        purchase.save()
        n = Notifications.objects.create(title='Purchase Approval',
        message=f'Purchase order {ref} approved by Purchase team',link = reverse_lazy('purchase',args=[ref]),)
        n.user.add(User.objects.get(user_type=3),tag='success')
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)

    
@api_view(['POST'])
def supplier_api(request):
    try:
        data = request.data
        ref = data['ref']
        status = data['status']
        draft = PurchaseDraft.objects.get(id=ref)
        status = Purchase_status(id=status)
        purchase = PurchaseOrder.objects.get(id=draft)
        purchase.status = status
        purchase.save()
        n = Notifications.objects.create(title='Supplier Update',
        message=f'Purchase order {ref} status update: {status}',link = reverse_lazy('purchase',args=[ref]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except Purchase_status.DoesNotExist:
        return Response({'error':'invalid status value'},status=404)