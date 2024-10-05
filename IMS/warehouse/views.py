from django.shortcuts import redirect,HttpResponse,HttpResponseRedirect
from django.template.response import TemplateResponse as render
from warehouse.models import Warehouse
from warehouse.forms import WarehouseForm
from datetime import datetime
from core.utils import manager_check,user_passes_test


# Create your views here.
def view_warehouse(request):
    warehouses = Warehouse.objects.all()
    return render(request,'warehouse/warehouses.html',{'warehouses':warehouses})


def get_warehouse(request,id):
    warehouse = Warehouse.objects.get(pk=id)
    return HttpResponse(warehouse)

@user_passes_test(manager_check)
def add_warehouse(request):
    edit = True
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(view_warehouse)
    else:
        form = WarehouseForm()
    return render(request,'warehouse/add_warehouse.html',{'form':form,'edit':edit})
    

@user_passes_test(manager_check)
def update_warehouse(request,id):
    i = Warehouse.objects.get(pk=id)
    edit = False
    if request.method == "POST":
        form = WarehouseForm(request.POST,instance=i)
        if form.is_valid():
            form.save()
            return redirect(view_warehouse)
        edit = True
    else:
        form = WarehouseForm(instance=i)
    return render(request,'warehouse/warehouse.html',{'form':form,'edit':edit})