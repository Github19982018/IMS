from django.template.response import TemplateResponse as render


# Create your views here.
def dashboard(request):
    return render(request,'dashboard.html',{})