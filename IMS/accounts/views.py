from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout

from accounts.forms import Registrationform,UserAuthenticationForm
from accounts.models import User

class RegistrationView(CreateView):
    model = User
    form_class = Registrationform
    template_name = 'registration.html'
    success_url = reverse_lazy('inventories')

    def form_valid(self,form):
        form.save()
        return super().form_valid(self,form)

        # if form.user_type == 'admin':
        #     self.success_url = reverse_lazy('dashboard')
    def form_invalid(self, form: BaseModelForm) :
        print(form.errors)
        return super().form_invalid(form)

# class UserLoginView(LoginView):
#     redirect_authenticated_user = True 
#     template_name = 'accounts/login.html'
#     success_url = reverse_lazy('inventories')
#     # authentication_form = UserAuthenticationForm

#     def form_valid(self,form):
#         userpass = authenticate(self,username=form.cleaned_data['username'],password=form.cleaned_data['password'])
#         if userpass is not None and userpass.user_type == 'admin':
#             self.success_url = reverse_lazy('dashboard')

#     def form_invalid(self, form):
#         return self.render_to_response(self.get_context_data(form=form))

def logins(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']
        #authenticate method checks the provided username and password against the database
        userpass = authenticate(request,username=username,password=password)
        if userpass:
            if user_type == '1' and userpass.is_superuser:
                login(request,userpass)
                request.session['admin_id']=userpass.id
                return redirect('/admin/',{'user':request.user})
            elif userpass.is_active:
                user = User.objects.get(id=userpass.id)
                if user_type=='2' and  user.user_type == 2:
                    login(request,userpass)
                    request.session['manager_id']=userpass.id
                    return redirect('dashboard')
                elif user_type == '3' and user.user_type == 3:
                    login(request,userpass)
                    request.session['specialist_id']=userpass.id
                    return redirect('inventories')
        
        return HttpResponse('invalid login')
        
    else:
        return render(request,'accounts/login.html')
        
        
