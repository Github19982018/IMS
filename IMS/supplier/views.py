from django.shortcuts import render,HttpResponse
from supplier.models import Supplier

# Create your views here.
def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request,template_name='suppliers.html',context={'data':suppliers})

def get_supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    return render(request,template_name='supplier.html',context={'data':supplier})