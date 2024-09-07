from django.shortcuts import render,HttpResponse
from datetime import datetime
from .models import Inventory,Supplier
# Create your views here.

def error_response_handler(request, exception=None):
    return HttpResponse('eror', status=404)

def view_inventory(request):
    inventory = Inventory.objects.all()
    return HttpResponse(inventory)

def get_inventory(request,id):
    inventory = Inventory.objects.get(pk=id)
    return HttpResponse(inventory)

def  add_inventory(request):
    # photo = models.FilePathField(unique=True,null=True,blank=True)
    name = 'test3'
    sku = '2'
    purchasing_price = 0
    selling_price = 0
    on_hand = 0
    description = 'test3'
    units = ''
    updated = datetime.now()
    brand = None
    # warehouse = ''
    # preferred_supplier = ''
    reorder_point = 0
    Inventory.objects.create(name=name,sku=sku,purchasing_price=purchasing_price,selling_price=selling_price,
                                         brand=brand,on_hand=on_hand,description=description,units=units,updated=updated,
                                         reorder_point=reorder_point)
    return HttpResponse('added succuessfully')

def update_inventory(request,id):
    inventory = Inventory.objects.get(pk=id)
    if request.method == 'POST':
        # photo = models.FilePathField(unique=True,null=True,blank=True)
        name = 'test3'
        sku = '2'
        purchasing_price = 0
        selling_price = 0
        on_hand = 0
        description = 'test3'
        units = ''
        updated = datetime.now()
        brand = None
        # warehouse = ''
        # preferred_supplier = ''
        reorder_point = 0
        inventory.update(name=name,sku=sku,purchasing_price=purchasing_price,selling_price=selling_price,
                                            brand=brand,on_hand=on_hand,description=description,units=units,updated=updated,
                                            reorder_point=reorder_point)
        return HttpResponse('added succuessfully')
    else:
        return HttpResponse(inventory)
    
