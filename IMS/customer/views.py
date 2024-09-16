from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from customer.models import Customer
from sales_orders.models import Sales
from django.contrib.auth.decorators import login_required

# Create your views here.

def specialist_auth(request):
    user = request.user
    if user.user_type == 3:
        return True
    else:
        raise PermissionError

@login_required
def view_customers(request):
    customers = Customer.objects.all()
    return render(request,'customers.html',{'customers':customers})

@login_required
def get_customer(request,id):
    customer = Customer.objects.get(id=id)
    orders = Sales.objects.filter(customer=customer)[:4]
    if request.method == 'POST':
        specialist_auth(request)
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