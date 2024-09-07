from django.shortcuts import render,HttpResponse
from supplier.models import Supplier

# Create your views here.
def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return HttpResponse(suppliers)

def get_supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    return HttpResponse(supplier)