from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from supplier.models import Supplier,Supplier_rating
from purchase_orders.models import PurchaseItems

# Create your views here.
def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request,'suppliers.html',{'suppliers':suppliers})

def get_supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    orders = PurchaseItems.objects.filter(supplier=supplier)
    if request.method == 'POST':
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