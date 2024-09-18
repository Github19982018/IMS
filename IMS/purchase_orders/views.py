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


def specialist_auth(request):
    user = request.user
    if user.user_type == 3:
        return True
    else:
        raise PermissionError


# Create your views here.
def view_purchases(request):
    purchases = PurchaseOrder.objects.filter(warehouse=request.w)
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
            w = request.w
            warehouse = Warehouse.objects.get(id=w)
            # warehouse = Warehouse.objects.all()
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
    if request.method == 'GET':
        i = Inventory.objects.get(id=id)
        purchase = PurchaseDraft.objects.create()
        draft = PurchaseItems.objects.create(purchase = purchase,
                item = i,
                price = i.selling_price,
                quantity = 1,
                units = i.units)
        return redirect(draft_purchase,id=purchase.id,permanent=True)
    else:
            return redirect('inventories')

@user_passes_test(specialilst_check)
def draft_purchase(request,id):
    if request.method == 'POST':
        quantity = request.POST.getlist('quantity')
        item = request.POST.getlist('item')
        for i in range(len(item)):
            sale = PurchaseItems.objects.get(id=item[i])
            sale.quantity = quantity[i]
            sale.save()
        return HttpResponseRedirect('')
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


def purchase(request,id):
    draft = PurchaseDraft.objects.get(id=id)
    if draft:
        items = PurchaseItems.objects.filter(purchase=draft)
        purchase = PurchaseOrder.objects.filter(id=draft)
        if purchase:
            return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase.first()})
        elif specialilst_check:
            if request.method == 'POST':
                total = 0
                for i in items:
                    total += i.total_price
                supplier = draft.supplier
                bill = request.POST['bill_address']
                ship = request.POST['ship_address']
                sh= request.POST['ship_method']
                ship_method = ShipMethod.objects.get(id=sh)
                p_date = request.POST['preferred_date']
                p_date = datetime.strptime(p_date,'%d/%m/%Y, %I:%M:%S %p')
                status = Purchase_status.objects.get(status='draft')
                purchase = PurchaseOrder.objects.create(id=draft,warehouse=Warehouse.objects.get(id=request.w),bill_address=bill,preferred_shipping_date=p_date ,ship_address=ship,contact_phone=supplier.phone,ship_method=ship_method,status=status,total_amount=total)
                return render(request,'purchase_next.html',{'number':id,'items':items, 'purchase':purchase})
            else:
                return render(request,'404.html',{})
    else:
        return render(request,'404.html',{})

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
        # its = {}
        # for i in items:
        #     item = its[i.item.name] = {}
        #     item['price'] = int(i.price)
        #     item['units'] = i.item.units
        #     item['quantity'] = i.quantity
        # data = {
        #     'ref':purchase.id.id,
        #     'supplier':purchase.id.supplier.name,
        #     'contact_person':purchase.id.supplier.contact_person,
        #     'bill_address':purchase.bill_address,
        #     'preferred_shipping_date':purchase.preferred_shipping_date.isoformat(),
        #     "ship_address":purchase.ship_address,
        #     'ship_method':purchase.ship_method.method,
        #     'contact_phone':int(purchase.contact_phone),
        #     'created_date':purchase.created_date.isoformat(),
        #     'total_amount':int(purchase.total_amount),
        #     "items":its
        # }
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
        n = Notifications.objects.create(title='Purchase Approval',
        message=f'Purchase order {ref} approved by Purchase team',link = reverse_lazy('purchase',args=[ref]),
        tag='success')
        n.user.add(User.objects.get(user_type=3))
        return Response({'data':'successfully updated'},status=201)
    except PurchaseDraft.DoesNotExist:
        return Response({'error':'order does not exist'},status=404)
    except Purchase_status.DoesNotExist:
        return Response({'error':'invalid status value'},status=404)