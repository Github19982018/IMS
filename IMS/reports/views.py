from django.template.response import TemplateResponse as render
from django.db.models import Sum,Avg,F,Count,Case,When
# Create your views here.
from purchase_orders.models import PurchaseStatus,PurchaseOrder,PurchaseItems
from sales_orders.models import SalesItems,Sales,SalesStatus,Shipment,Package,PackageStatus,ShipStatus
from inventory.models import Inventory
from customer.models import Customer
from supplier.models import Supplier
from django.db import connection
from core.utils import manager_check,user_passes_test

from django.db import connection
cursor = connection.cursor()

def reports(request):
    return render(request,'reports.html',{})

@user_passes_test(manager_check)
def purchase(request):
    filterby = request.GET.get('by')
    purchases = ''
    if filterby == 'item':
        purchases = PurchaseItems.objects.values('item','item__name').annotate(amount=Sum('price'),quantity=Sum('quantity'),price=Avg('price'))
    return render(request,'report_purchase.html',{'purchase':purchases})

@user_passes_test(manager_check)
def sales(request):
    filterby = request.GET.get('by')
    if filterby == 'item':
        sales = SalesItems.objects.values('item','item__name').annotate(amount=Sum('price'),price=Avg('price'),quantity=Sum('quantity'))
        return render(request,'report_sales.html',{'sales':sales})
    elif filterby == 'customer':
        sales = SalesItems.objects.values('sales__customer','item__name','sales__customer__name').annotate(amount=Sum('price'),price=Avg('price'),quantity=Sum('quantity'))
        return render(request,'report_sales_customer.html',{'sales':sales})


@user_passes_test(manager_check)
def inventory(request):
    cursor.execute( """select sum(quantity) from purchase_orders_purchaseitems pi join purchase_orders_purchasedraft pd on pi.purchase_id=pd.id join purchase_orders_purchaseorder po on pd.id=po.id_id where po.status_id=6 and po.cancel=false and po.warehouse_id=%s; """,(request.w,))
    ((to_receive,),) = cursor.fetchall()
    # inventory = Inventory.objects.values('name').filter(purchase__order__status=1).annotate(ordered=Sum('on_hand')) 
    # return render(request,'report_inventory.html',{'inventory':inventory})
    # sales = SalesItems.objects.filter(sales__status__id=6) 
    # p_order = PurchaseItems.objects.filter(purchase__order__status__in=[4,5,6],purchase__order__cancel=False)
    # p_in = PurchaseItems.objects.filter(purchase__receive__status=3,purchase__order__cancel=False)
    # Inventory.objects.select_related('purchase__order','sales__order','purchase__receive').values('name').annotate(ordered=Count('purchase__cancel=False and purchase__status=3'),Qunatity_out=Count('sales__status=6'),Qunatity_in=Count('purchase__cancel=False and recieve__status=3'))   
    # Inventory.objects.select_related('purchase__order','sales__order','purchase__receive').annotate(ordered=Count('purchase__cancel=false'))
    # cursor.execute( """select sum(quantity) from inventory_inventory i join  purchase_orders_purchaseitems pi join purchase_orders_purchasedraft pd on pi.purchase_id=pd.id join purchase_orders_purchaseorder po on pd.id=po.id_id where po.status_id=6 and po.cancel=false and po.warehouse_id=%s; """,(request.w,))
    # ((to_receive,),) = cursor.fetchall()
    return render(request,'404.html',{'inventory':inventory})
    
    