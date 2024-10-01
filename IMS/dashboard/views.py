from django.template.response import TemplateResponse as render
from sales_orders.models import Package,PackageStatus,Sales,SalesStatus,Shipment,ShipStatus,SalesItems
from inventory.models import Inventory
from django.db.models.lookups import GreaterThan,LessThan
from django.db.models import Sum
from purchase_orders.models import PurchaseOrder,PurchaseStatus,PurchaseItems,PurchaseDraft
from django.db import connection
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

# Create your views here.
def dashboard(request):
    pack = Package.objects.filter(status=PackageStatus(id=PACKAGE_DRAFT)).count()
    ship = Shipment.objects.filter(status__in=ShipStatus.objects.filter(id__in=[0,1,2])).count()
    deliver = Shipment.objects.filter(status=ShipStatus(id=CARRIER_PICKED)).count()
    on_hand = Inventory.objects.aggregate(on_hand=Sum('on_hand'))
    # to_receive = PurchaseItems.objects.aggregate(Sum('quantity'))
    cursor.execute( """select sum(quantity) from purchase_orders_purchaseitems pi join purchase_orders_purchasedraft pd on pi.purchase_id=pd.id join purchase_orders_purchaseorder po on pd.id=po.id_id where po.status_id<7; """)
    ((to_receive,),) = cursor.fetchall()
    
    purchase_items = PurchaseItems.objects.values('item').distinct().count()
    purchase_quantity = PurchaseItems.objects.aggregate(purchase_quantity=Sum('quantity'))
    purchase_amount = PurchaseOrder.objects.aggregate(purchase_amount=Sum('total_amount'))
    # print(purchase_amount,purchase_quantity)
    total_stock = Inventory.objects.all().count()
    draft = Sales.objects.filter(status=SalesStatus(id=SALE_DRAFT)).count()
    packed = Sales.objects.filter(status__in=SalesStatus.objects.filter(id__in=[2,3,4,5])).count()
    shipped = Sales.objects.filter(status__in=SalesStatus.objects.filter(id__in=[3,4,5])).count()
    # cursor.execute('''SELECT count(id) FROM purchase where id>0 and id<)

    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<(reorder_point) and (on_hand>0)''')
    # low_stock = Inventory.objects.raw('''SELECT count(id) FROM inventory_inventory where on_hand<(reorder_point) and (on_hand>0)''')
    # low_stock = Inventory.objects.aaggregate(F('on_hand'))
    ((low_stock,),) = cursor.fetchall()
    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<=0''')
    # no_stock = Inventory.objects.raw('''SELECT count(id) FROM inventory_inventory where on_hand<=0''')
    ((no_stock,),)= cursor.fetchall()
    in_stock = total_stock - (low_stock + no_stock)
    sales = Sales.objects.all().order_by('-updated')
    purchases = PurchaseOrder.objects.all().order_by('-updated')
    total_purchases = [int(i.total_amount) if i.total_amount is not None else 0 for i in purchases ]
    total_sales = [int(i.total_amount) if i.total_amount is not None else 0 for i in sales ]
    # total_sales = [i for i in range(3,56,2)]
    recent_sales = sales[:4]
    top_selling = SalesItems.objects.raw("""SELECT *,(sum(quantity*price)) as amount from sales_orders_salesitems  group by item_id ORDER BY amount desc LIMIT 5 ;""")
    import json
    stock = json.dumps({'Low Stock':low_stock, 'No Stock':no_stock,'In Stock':in_stock})
    # stock=[43,56,22]
    sales = json.dumps({'Packed':packed,'shipped':shipped,'draft':draft})
    return render(request,'dashboard.html',{'sales_activity':{'pack':pack,'ship':ship,'deliver':deliver},'sales':sales,
                                            'inventory':{'on_hand':on_hand,'recieve':to_receive,
                                                         'top_selling':top_selling},'stock': stock,'purchase':{'items':purchase_items,
                                                                            'quantity':purchase_quantity['purchase_quantity'],
                                                                            'amount':purchase_amount['purchase_amount']},
                                            'recent_sales':recent_sales, 'total_sales':total_sales,'total_purchases':total_purchases,'sales_orders':{

                                            }})
    