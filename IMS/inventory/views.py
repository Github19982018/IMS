from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,redirect,HttpResponseRedirect
from datetime import datetime
from inventory.models import Inventory,Supplier
from warehouse.models import Warehouse
from inventory.forms import InventoryForm
# Create your views here.
from core.utils import specialilst_check,user_passes_test,date_filter

def error_response_handler(request, exception=None):
    return HttpResponse('eror', status=404)

""



def view_inventory(request):
    w = request.w
    date = request.GET.get('date','year')
    warehouse = Warehouse.objects.get(id=w)
    order_by = request.GET.get('orderby')
    filter = request.GET.get('filter')
    inventory = Inventory.objects.filter(warehouse=warehouse)
    if filter:
        inventory = inventory.filter(filter)
    if order_by:
        inventory = inventory.order_by(order_by)
    inventory = date_filter(date,inventory)
    return render(request,'inventory/inventory.html',{'inventory':inventory})


@user_passes_test(specialilst_check)
def add_inventory(request):
    if request.method == "POST":
        f = InventoryForm(request.POST, request.FILES)
        print(f.errors)
        if f.is_valid():
            f.updated = datetime.now()
            f.save()
            return redirect(view_inventory)
        else:
            return HttpResponse('error')
    else:
        supplier = Supplier.objects.all()
        warehouses = Warehouse.objects.all()
        form = InventoryForm()
        return render(request,'inventory/additem.html',{'form':form,'supplier':supplier,'warehouses':warehouses})

@user_passes_test(specialilst_check)
def update_inventory(request,id):
    try:
        i = Inventory.objects.get(pk=id)
    except Inventory.DoesNotExist:
        return render(request,'404.html')
    if request.method == "POST":
        f = InventoryForm(request.POST, request.FILES, instance=i)
        if f.is_valid():
            f.updated = datetime.now()
            f.save()
            return redirect(view_inventory)
        else:
            return HttpResponseRedirect('')
    else:
        return inventory(request,id)
    
        
def inventory(request,id):
    try:
        i = Inventory.objects.get(pk=id)
        supplier = Supplier.objects.all()
        warehouses = Warehouse.objects.all()
        form = InventoryForm(instance=i)
        return render(request,'inventory/item.html',{'form':form,'supplier':supplier,'warehouses':warehouses})
    except Inventory.DoesNotExist:
        return render(request,'404.html')
    
# def  add_inventory(request):
#     # photo = models.FilePathField(unique=True,null=True,blank=True)
#     name = request
#     sku = '2'
#     purchasing_price = 0
#     selling_price = 0
#     on_hand = 0
#     description = 'test3'
#     units = ''
#     updated = datetime.now()
#     brand = None
#     # warehouse = ''
#     # preferred_supplier = ''
#     reorder_point = 0
#     Inventory.objects.create(name=name,sku=sku,purchasing_price=purchasing_price,selling_price=selling_price,
#                                          brand=brand,on_hand=on_hand,description=description,units=units,updated=updated,
#                                          reorder_point=reorder_point)
#     return HttpResponse('added succuessfully')

# def update_inventory(request,id):
#     inventory = Inventory.objects.get(pk=id)
#     if request.method == 'POST':
#         # photo = models.FilePathField(unique=True,null=True,blank=True)
#         name = 'test3'
#         sku = '2'
#         purchasing_price = 0
#         selling_price = 0
#         on_hand = 0
#         description = 'test3'
#         units = ''
#         updated = datetime.now()
#         brand = None
#         # warehouse = ''
#         # preferred_supplier = ''
#         reorder_point = 0
#         inventory.update(name=name,sku=sku,purchasing_price=purchasing_price,selling_price=selling_price,
#                                             brand=brand,on_hand=on_hand,description=description,units=units,updated=updated,
#                                             reorder_point=reorder_point)
#         return HttpResponse('added succuessfully')
#     else:
#         return HttpResponse(inventory)
    
    
