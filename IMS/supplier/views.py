from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from supplier.models import Supplier
from purchase_orders.models import Purchase

# Create your views here.
def view_suppliers(request):
    suppliers = Supplier.objects.all()
    return render(request,template_name='suppliers.html',context={'suppliers':suppliers})

def get_supplier(request,id):
    supplier = Supplier.objects.get(id=id)
    orders = Purchase.objects.filter(supplier=supplier)
    if request.method == 'POST':
        rating = supplier.rating
        rating.commitment = request.POST['commitment']
        rating.consistency = request.POST['consistency']
        rating.transaction = request.POST['transaction']
        rating.cost = request.POST['cost']
        rating.competency = request.POST['competency']
        rating.communication = request.POST['communication']
        rating.save()
        return HttpResponseRedirect('')
    else:
        return render(request,template_name='supplier.html',context={'supplier':supplier,'orders':orders})