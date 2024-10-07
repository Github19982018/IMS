from django.template.response import TemplateResponse as render
from django.shortcuts import HttpResponse,HttpResponseRedirect
from customer.models import Customer
from sales_orders.models import Sales
from core.utils import specialilst_check

# Create your views here.

def view_customers(request):
    customers = Customer.objects.all()
    return render(request,'customers.html',{'customers':customers})

def get_customer(request,id):
    try:
        customer = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        return render(request,'404.html',status=404)
    orders = Sales.objects.filter(customer=customer)[:4]
    return render(request,'Customer.html',{'customer':customer,'orders':orders})
    
def customer_orders(request,id):
    try:
        customer = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        return render(request,'404.html',status=404)
    orders = Sales.objects.filter(customer=customer)
    return render(request,'sales_orders/sales.html',{'sales':orders})