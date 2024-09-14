from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse as render
from sales_orders.models import Package,PackageStatus,Sales,SalesStatus,Shipment,ShipStatus,SalesItems
from inventory.models import Inventory
from django.db.models.lookups import GreaterThan,LessThan
from django.db.models import Sum
from purchase_orders.models import PurchaseOrder,Purchase_status,PurchaseItems
from django.db import connection

# Create your views here.
@login_required
def dashboard(request):
    pack = Package.objects.filter(status=PackageStatus(id=1)).count()
    ship = Shipment.objects.filter(status=ShipStatus(id=1)).count()
    deliver = Shipment.objects.filter(status=ShipStatus(id=4)).count()
    on_hand = Inventory.objects.aggregate(on_hand=Sum('on_hand'))
    to_receive = PurchaseOrder.objects.filter(status__in=[4,5]).count()
    purchase_items = PurchaseItems.objects.all().values('item_id').distinct().count()
    purchase_quantity = PurchaseItems.objects.aggregate(purchase_quantity=Sum('quantity'))
    purchase_amount = PurchaseOrder.objects.aggregate(purchase_amount=Sum('total_amount'))
    # print(purchase_amount,purchase_quantity)
    total_stock = Inventory.objects.all().count()
    cursor = connection.cursor()
    draft = PurchaseOrder.objects.filter(status=Purchase_status(id=1)).count()
    packed = PurchaseOrder.objects.filter(status=Purchase_status(id=3)).count()
    shipped = PurchaseOrder.objects.filter(status=Purchase_status(id=5)).count()
    packed,shipped,draft = 6,3,7
    # cursor.execute('''SELECT count(id) FROM purchase where id>0 and id<)

    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<(reorder_point) and (on_hand>0)''')
    ((low_stock,),) = cursor.fetchall()
    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<=0''')
    ((no_stock,),)= cursor.fetchall()
    in_stock = total_stock - (low_stock + no_stock)
    sales = Sales.objects.all().order_by('-updated')
    total_sales = [i.total_amount for i in sales]
    total_sales = [i for i in range(3,56,2)]
    recent_sales = sales[:4]
    top_selling = SalesItems.objects.raw("""SELECT *,(sum(quantity)*price) as amount from sales_orders_salesitems  group by item_id ORDER BY amount desc LIMIT 5 ;""")
    import json
    print(purchase_amount['purchase_amount'])
    stock = json.dumps({'low_stock':low_stock, 'no_stock':no_stock,'in_stock':in_stock})
    # stock=[43,56,22]
    sales = json.dumps({'Packed':packed,'shipped':shipped,'draft':draft})
    cursor.close()
    return render(request,'dashboard.html',{'sales_activity':{'pack':pack,'ship':ship,'deliver':deliver},'sales':sales,
                                            'inventory':{'on_hand':on_hand,'recieve':to_receive,
                                                         'top_selling':top_selling},'stock': stock,'purchase':{'items':purchase_items,
                                                                            'quantity':purchase_quantity['purchase_quantity'],
                                                                            'amount':purchase_amount['purchase_amount']},
                                            'recent_sales':recent_sales, 'total_sales':total_sales,'sales_orders':{

                                            }})
    