import json
from django.template.response import TemplateResponse as render
from sales_orders.models import Package,PackageStatus,Sales,SalesStatus,Shipment,ShipStatus,SalesItems
from inventory.models import Inventory,Warehouse
from django.db.models.lookups import GreaterThan,LessThan
from django.db.models import Sum,Q
from datetime import datetime,timedelta
from purchase_orders.models import PurchaseOrder,PurchaseStatus,PurchaseItems,PurchaseDraft
from django.db import connection
from core.utils import user_passes_test,manager_check
cursor = connection.cursor()

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
@user_passes_test(manager_check)
def dashboard(request):
    date = request.GET.get('date','month')
    warehouse = Warehouse.objects.get(id=request.w) or Warehouse.objects.first()
    pack = Package.objects.filter(status=PackageStatus.objects.get(id=PACKAGE_DRAFT))
    pack = date_filter(date,pack).count()
    ship = Sales.objects.filter(warehouse=warehouse,status=SalesStatus.objects.get(id=SALE_PACKED))
    ship = date_filter(date,ship).count()
    deliver = Sales.objects.filter(warehouse=warehouse,status=SalesStatus.objects.get(id=SALE_SHIPPED))
    deliver = date_filter(date,deliver).count()
    on_hand = Inventory.objects.filter(warehouse=warehouse,).aggregate(on_hand=Sum('on_hand'))
    cursor.execute( """select sum(quantity) from purchase_orders_purchaseitems pi join purchase_orders_purchasedraft pd on pi.purchase_id=pd.id join purchase_orders_purchaseorder po on pd.id=po.id_id where po.status_id=6 and po.cancel=false and po.warehouse_id=%s; """,(request.w,))
    ((to_receive,),) = cursor.fetchall()
    
    cursor.execute( """select count(distinct pi.id), sum(quantity),sum(total_amount) from purchase_orders_purchaseitems pi join purchase_orders_purchasedraft pd on pi.purchase_id=pd.id join purchase_orders_purchaseorder po on pd.id=po.id_id where po.status_id<7 and po.status_id>2 and po.cancel=false and po.warehouse_id=%s; """,(request.w,))
    ((purchase_items,purchase_quantity,purchase_amount),) = cursor.fetchall()
    total_stock = Inventory.objects.all().count()
    draft = Sales.objects.filter(status=SalesStatus(id=SALE_DRAFT))
    draft = date_filter(date,draft).count()
    packed = Sales.objects.filter(status__in=SalesStatus.objects.filter(id__in=[2,3,4,5]))
    packed = date_filter(date,packed).count()
    shipped = Sales.objects.filter(status__in=SalesStatus.objects.filter(id__in=[3,4,5]))
    shipped = date_filter(date,shipped).count()

    cursor.execute('''SELECT count(i.id) FROM inventory_inventory i join inventory_inventory_warehouse iw on iw.inventory_id=i.id where on_hand<(reorder_point) and (on_hand>0) and iw.warehouse_id=%s''',(warehouse.id,))
    ((low_stock,),) = cursor.fetchall()
    cursor.execute('''SELECT count(i.id) FROM inventory_inventory i join inventory_inventory_warehouse iw on iw.inventory_id=i.id where on_hand<=0 and iw.warehouse_id=%s''',(warehouse.id,))
    # no_stock = Inventory.objects.raw('''SELECT count(id) FROM inventory_inventory where on_hand<=0''')
    ((no_stock,),)= cursor.fetchall()
    in_stock = total_stock - (low_stock + no_stock)
    sales = Sales.objects.filter(warehouse=warehouse).order_by('-updated')
    sales=date_filter(date,sales)
    purchases = PurchaseOrder.objects.filter(warehouse=warehouse).order_by('-updated')
    purchases=date_filter(date,purchases)
    total_purchases = [int(i.total_amount) if i.total_amount is not None else None for i in purchases ]
    total_sales = [int(i.total_amount) if i.total_amount is not None else None for i in sales ]
    report_date = []
    if purchases:     
        if date == 'today':
            start = min(purchases.last().updated.hour,sales.last().updated.hour)
            end = max(purchases[0].updated.hour,sales[0].updated.hour)
            report_date = [i for i in range(start,end+1,1)]
        elif date=='month':
            start = min(purchases.last().updated.day,sales.last().updated.day)
            end = max(purchases[0].updated.day,sales[0].updated.day)
            report_date = [i for i in range(start,end+1,1)]
        elif date=='year':
            start = min(purchases.last().updated.month,sales.last().updated.month)
            end = max(purchases[0].updated.month,sales[0].updated.month)
            report_date = [i for i in range(start,end+1,1)]
        elif date=='week':
            start = min(purchases.last().updated.weekday(),sales.last().updated.weekday())
            end = max(purchases[0].updated.weekday(),sales[0].updated.weekday())
            report_date = [i for i in range(start,end+1,1)]
    else:
         report_date =[0]
    report_date = json.dumps(report_date)
    recent_sales = sales[:4]
    top_selling = SalesItems.objects.raw("""SELECT *,(sum(quantity*price)) as amount from sales_orders_salesitems si join sales_orders_sales s on si.sales_id=s.id where s.warehouse_id=%s group by item_id ORDER BY amount desc LIMIT 5 ;""",(request.w,))
    stock = json.dumps({'Low Stock':low_stock, 'No Stock':no_stock,'In Stock':in_stock})
    sales = json.dumps({'Packed':packed,'shipped':shipped,'draft':draft})
    return render(request,'dashboard.html',{'sales_activity':{'pack':pack or 0,'ship':ship or 0,'deliver':deliver or 0},'sales':sales,
                                            'inventory':{'on_hand':on_hand or 0,'recieve':to_receive or 0,
                                                         'top_selling':top_selling},'stock': stock,'purchase':{'items':purchase_items or 0,
                                                                            'quantity':purchase_quantity or 0,
                                                                            'amount':purchase_amount or 0},
                                            'recent_sales':recent_sales,'date':date, 'total_sales':total_sales,'total_purchases':total_purchases,'reports_y':report_date ,'sales_orders':{

                                            }})
    