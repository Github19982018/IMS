from django.contrib.auth.decorators import user_passes_test  #DONT DELETE!!!  imported in other apps 
from datetime import datetime

def specialilst_check(user):
    return user.user_type == 3

def manager_check(user):
    return user.user_type == 2


def date_filter(date,queryset):
    day = datetime.now().day
    year = datetime.now().year
    month = datetime.now().month
    week = datetime.now().isocalendar()[1]
    if date=='today':
        queryset = queryset.filter(updated__day=day)
    if date == 'month':
        queryset = queryset.filter(updated__month=month)
    elif date == 'year':
        queryset = queryset.filter(updated__year=year)
    elif date == 'week':
        queryset = queryset.filter(updated__week=week)
    return queryset