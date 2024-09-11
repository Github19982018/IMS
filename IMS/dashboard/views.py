from django.template.response import TemplateResponse as render
from sales_orders.models import Package,Package_status,Sales,Sales_status,Shipment,Ship_status,Sales_items
from inventory.models import Inventory
from django.db.models.lookups import GreaterThan,LessThan
from django.db.models import Sum
from purchase_orders.models import Purchase,Purchase_status
from django.db import connection

# Create your views here.
def dashboard(request):
    pack = Package.objects.filter(status=Package_status(id=1)).count()
    ship = Shipment.objects.filter(status=Ship_status(id=1)).count()
    deliver = Shipment.objects.filter(status=Ship_status(id=4)).count()
    on_hand = Inventory.objects.aggregate(on_hand=Sum('on_hand'))
    to_receive = Purchase.objects.filter(status__in=[4,5]).count()
    # purchase_orders = Purchase.objects.aaggregate(purchase_orders=Sum(''))
    purchase_amount = Purchase.objects.aggregate(purchase_amount=Sum('total_amount'))
    total_stock = Inventory.objects.all().count()
    cursor = connection.cursor()
    draft = Purchase.objects.filter(status=Purchase_status(id=1))
    packed = Purchase.objects.filter(status=Purchase_status(id=3))
    shipped = Purchase.objects.filter(status=Purchase_status(id=5))
    # cursor.execute('''SELECT count(id) FROM purchase where id>0 and id<)

    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<(reorder_point or 15)''')
    ((low_stock,),) = cursor.fetchall()
    cursor.execute('''SELECT count(id) FROM inventory_inventory where on_hand<=0''')
    ((no_stock,),)= cursor.fetchall()
    in_stock = total_stock - (low_stock + no_stock)
    sales = Sales.objects.all().order_by('-updated')
    total_sales = [i.total_amount for i in sales]
    total_sales = [i for i in range(3,56,2)]
    recent_sales = sales[:4]
    top_selling = Sales_items.objects.raw("""SELECT *,sum(quantity) AS total,(sum(quantity)*price) as amount from sales_orders_sales_items  group by item_id_id ORDER BY total desc LIMIT 5 ;""")
    import json
    stock = json.dumps({'low_stock':low_stock, 'no_stock':no_stock,'in_stock':in_stock})
    cursor.close()
    return render(request,'dashboard.html',{'sales_activity':{'pack':pack,'ship':ship,'deliver':deliver,
                                            'Packed':packed,'shipped':shipped,'draft':draft},
                                            'inventory':{'on_hand':on_hand,'recieve':to_receive,
                                                         'top_selling':top_selling},'stock': stock,
                                            'purchase_amount':purchase_amount,'recent_sales':recent_sales, 'total_sales':total_sales,'sales_orders':{

                                            }})
    