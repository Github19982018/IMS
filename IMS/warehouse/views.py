from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from warehouse.models import Warehouse
from warehouse.forms import WarehouseForm
from datetime import datetime


# Create your views here.
def view_warehouse(request):
    user = request.user
    if user.user_type == 1:
        order_by = request.GET.get('orderby')
        filter = request.GET.get('filter')
        warehouses = Warehouse.objects.all()
        if filter:
            warehouses = warehouses.filter()
        if order_by:
            warehouses = warehouses.order_by(order_by)
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