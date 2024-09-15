from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from warehouse.models import Warehouse
from warehouse.forms import WarehouseForm
from datetime import datetime


# Create your views here.
def view_warehouse(request):
    user = request.user
    # if user.user_type == 1:
    warehouses = Warehouse.objects.all()
    return render(request,'warehouse/warehouses.html',{'warehouses':warehouses})

def get_warehouse(request,id):
    warehouse = Warehouse.objects.get(pk=id)
    return HttpResponse(warehouse)

def add_warehouse(request):
    if request.method == "POST":
        f = WarehouseForm(request.POST)
        f.save()
        return redirect(view_warehouse)
    else:
        form = WarehouseForm()
        return render(request,'warehouse/warehouse.html',{'form':form})
    
def update_warehouse(request,id):
    i = Warehouse.objects.get(pk=id)
    if request.method == "POST":
        f = WarehouseForm(request.POST,instance=i)
        if f.is_valid:
            f.save()
            return redirect(view_warehouse)
        else:
            return HttpResponseRedirect('')
    else:
        form = WarehouseForm(instance=i)
        return render(request,'warehouse/warehouse.html',{'form':form})