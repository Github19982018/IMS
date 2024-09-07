from django.shortcuts import render
from purchase_orders.models import Purchase,Purchase_status

# Create your views here.
def view_purchases(request):
    purchases = Purchase.objects.all()
    return render(request,template_name='purchases.html',context={'purchases':purchases})

def add_purchase(request):
    return render(request,template_name='purchase.html')