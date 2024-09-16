from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from customer.models import Customer
from sales_orders.models import Sales

# Create your views here.
def view_customers(request):
    customers = Customer.objects.all()
    return render(request,'customers.html',{'customers':customers})

def get_customer(request,id):
    customer = Customer.objects.get(id=id)
    orders = Sales.objects.filter(customer=customer)
    if request.method == 'POST':
        commitment = request.POST['commitment']
        consistency = request.POST['consistency']
        transaction = request.POST['transaction']
        cost = request.POST['cost']
        competency = request.POST['competency']
        communication = request.POST['communication']
        # rating = Customer_rating(commitment=commitment,
        # consistency=consistency,transaction=transaction,cost=cost,competency=competency,
        # communication=communication)
        # Customer.rating = rating
        # rating.save()
        customer.save()
        return HttpResponseRedirect('')
    else:
        return render(request,'Customer.html',{'customer':customer,'orders':orders})