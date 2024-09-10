from django import template
register = template.Library()

@register.filter()
def add_items(items, extra=0):
    sum = 0
    for i in items:
        sum += (i.quantity*i.price)
    sum += extra
    return sum
