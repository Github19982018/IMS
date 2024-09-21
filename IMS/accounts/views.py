from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect,HttpResponseRedirect
from django.template.response import TemplateResponse as render
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash

from django.contrib.auth.decorators import login_not_required

from accounts.forms import Registrationform,Updateform,PasswordChangeForm
from accounts.models import User
from django.contrib import messages

class RegistrationView(CreateView):
    model = User
    form_class = Registrationform
    template_name = 'registration.html'
    success_url = reverse_lazy('inventories')

    def form_valid(self,form):
        instance = form.save(commit=False)
        instance.is_active = False
        instance.save()
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
@login_not_required
def logins(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']
        #authenticate method checks the provided username and password against the database
        userpass = authenticate(request,username=username,password=password)
        if userpass:
            if user_type == '1' and userpass.is_superuser:
                user = User.objects.get(id=userpass.id)
                login(request,userpass)
                print(request.user.pk)
                request.session['user']=userpass.id
                return redirect(to=reverse_lazy('admin:index'),context={'user':request.user})
            elif userpass.is_active:
                user = User.objects.get(id=userpass.id)
                if user_type=='2' and  user.user_type == 2:
                    login(request,user)
                    request.session['manager_id']=userpass.id
                    return redirect('dashboard')
                elif user_type == '3' and user.user_type == 3:
                    login(request,userpass)
                    request.session['specialist_id']=userpass.id
                    return redirect('inventories')
        
        return HttpResponse('invalid login')
        
    else:
        return render(request,'accounts/login.html')
    

def profile(request):
    if request.method == 'POST':
        user_form = Updateform(request.POST,request.FILES, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request,'Your Profile is updated succuessfully !')
            return redirect(profile)
        else:
            messages.error(request,'Error in input data')
            print(user_form.errors)
    else:
        user_form = Updateform(instance=request.user)
    return render(request,'accounts/profile.html',{'USER':request.user,'userform':user_form})

    user_id = request.user.id
    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        userform = Userform(request.POST,instance=request.user)
        print(userform.errors)
        if userform.is_valid():
            userform.save()
    return render(request,'accounts/profile.html',{'USER':user})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user,request.POST)
        print(form.errors)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request,user)
            messages.success(request,'Your password was succuessfully updated!')
            return redirect(profile)
        else:
            messages.error(request,'Please correct the error below.')
    else:
        form =PasswordChangeForm(request.user)

    return render(request,'accounts/profile.html',{'USER':request.user,'form':form})

        
        
