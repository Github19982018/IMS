from django.template.response import TemplateResponse as render
from django.shortcuts import redirect
from supplier.models import Supplier,Supplier_rating
from purchase_orders.models import PurchaseDraft,PurchaseOrder
from core.utils import specialilst_check
# Create your views here.


def supplier_rating(data,supplier):
    commitment = data['commitment']
    consistency = data['consistency']
    transaction = data['transaction']
    cost = data['cost']
    competency = data['competency']
    communication = data['communication']
    rating = Supplier_rating(commitment=commitment,
    consistency=consistency,transaction=transaction,cost=cost,competency=competency,
    communication=communication)
    supplier.rating = rating
    rating.save()
    supplier.save()
    return


def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request,'suppliers.html',{'suppliers':suppliers})

def supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    orders = PurchaseDraft.objects.filter(supplier=supplier)[:4]
    if request.method == 'POST' and specialilst_check:
        supplier_rating(request.POST,supplier)
        return redirect('supplier',id=id)
    else:
        return render(request,'supplier.html',{'supplier':supplier,'orders':orders})
    
    
def supplier_orders(request,id):
    supplier = Supplier.objects.get(id=id)
    purchases = PurchaseOrder.objects.filter(id__supplier=supplier)
    return render(request,'purchases.html',{'purchases':purchases})

