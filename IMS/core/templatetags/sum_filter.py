from django import template
register = template.Library()

@register.filter
def add_items(items, extra=0):
    sum = 0
    for i in items:
        sum += (i.quantity*i.price)-(i.quantity*i.price*i.discount/100)
    sum += extra
    return sum

@register.filter
def add_p_items(items, extra=0):
    sum = 0
    for i in items:
        sum += (i.quantity*i.price)
    sum += extra
    return sum


@register.filter
def date_filter(date, extra=0):
    if date =='today':
        return "Today"
    elif date == 'month':
        return 'This month'
    elif date == 'year':
        return 'This year'

