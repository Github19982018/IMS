from django.contrib.auth.decorators import user_passes_test  #DONT DELETE!!!  imported in other apps 

def specialilst_check(user):
    return user.user_type == 3

def manager_check(user):
    return user.user_type == 2