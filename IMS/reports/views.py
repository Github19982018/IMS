from django.template.response import TemplateResponse as render
from django.db.models import Sum,Avg,F
# Create your views here.
from purchase_orders.models import Purchase_status,PurchaseOrder,PurchaseItems
from sales_orders.models import SalesItems,Sales,SalesStatus,Shipment,Package,PackageStatus,ShipStatus
from inventory.models import Inventory
from customer.models import Customer
from supplier.models import Supplier


def reports(request):
    return render(request,'reports.html',{})

def purchase(request):
    filterby = request.GET.get('by')
    purchases = ''
    if filterby == 'item':
        purchases = PurchaseItems.objects.values('item_id').annotate(amount=Sum('price'),quantity=Sum('quantity'),price=Avg('price'))
    return render(request,'report_purchase.html',{'purchase':purchases})

def sales(request):
    filterby = request.GET.get('by')
    if filterby == 'item':
        sales = SalesItems.objects.values('item_id','item_id__name').annotate(amount=Sum('price'),price=Avg('price'),quantity=Sum('quantity'))
    elif filterby == 'customer':
        sales = SalesItems.objects.values('customer','item_id__name','customer__name').annotate(amount=Sum('price'),price=Avg('price'),quantity=Sum('quantity'))
    return render(request,'report_sales_customer.html',{'sales':sales})


def inventory(request):
    inventory = Inventory.objects.values('name').annotate(ordered=Sum('on_hand')).filter(purchase__order__status=1)
    
    return render(request,'report_inventory.html',{'inventory':inventory})
    
    