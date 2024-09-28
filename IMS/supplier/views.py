from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from supplier.models import Supplier,Supplier_rating
from purchase_orders.models import PurchaseDraft,PurchaseOrder
from core.utils import specialilst_check
# Create your views here.


def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request,'suppliers.html',{'suppliers':suppliers})

def get_supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    orders = PurchaseDraft.objects.filter(supplier=supplier)[:4]
    if request.method == 'POST' and specialilst_check:
        commitment = request.POST['commitment']
        consistency = request.POST['consistency']
        transaction = request.POST['transaction']
        cost = request.POST['cost']
        competency = request.POST['competency']
        communication = request.POST['communication']
        rating = Supplier_rating(commitment=commitment,
        consistency=consistency,transaction=transaction,cost=cost,competency=competency,
        communication=communication)
        supplier.rating = rating
        rating.save()
        supplier.save()
        return HttpResponseRedirect('')
    else:
        return render(request,'supplier.html',{'supplier':supplier,'orders':orders})
    
    
def supplier_orders(request,id):
    supplier = Supplier.objects.get(id=id)
    purchases = PurchaseOrder.objects.filter(id__supplier=supplier)
    return render(request,'purchases.html',{'purchases':purchases})