from django.template.response import TemplateResponse as render
from django.db.models import Sum,Avg,F
# Create your views here.
from purchase_orders.models import PurchaseStatus,PurchaseOrder,PurchaseItems
from sales_orders.models import SalesItems,Sales,SalesStatus,Shipment,Package,PackageStatus,ShipStatus
from inventory.models import Inventory
from customer.models import Customer
from supplier.models import Supplier
from core.utils import manager_check,user_passes_test

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
    elif filterby == 'customer':
        sales = SalesItems.objects.values('sales__customer','item__name','sales__customer__name').annotate(amount=Sum('price'),price=Avg('price'),quantity=Sum('quantity'))
    return render(request,'report_sales_customer.html',{'sales':sales})


@user_passes_test(manager_check)
def inventory(request):
    # inventory = Inventory.objects.values('name').filter(purchase__order__status=1).annotate(ordered=Sum('on_hand')) 
    # return render(request,'report_inventory.html',{'inventory':inventory})
    return render(request,'404.html',{'inventory':inventory})
    
    