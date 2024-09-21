from inventory.models import Warehouse
from django.contrib.auth.decorators import login_required
from core.models import Notifications


class Warehouse_middleware:
    wa = Warehouse.objects.all().first().id
    with open('data/warehouse.txt','+w') as wfile:
        wfile.write(str(wa))

    def __init__(self,get_response): 
        self.get_response = get_response
        with open('data/warehouse.txt','r+') as wfile:
            self.warehouse = wfile.read()
            
    def __call__(self, request):
        self.warehouse = request.GET.get('warehouse') or self.warehouse
        with open('data/warehouse.txt','+w') as wfile:
            wfile.write(self.warehouse)
        request.w = self.warehouse
        response = self.get_response(request)
        return response
    
    # @login_required
    def process_template_response(self,request, response):
        warehouses = Warehouse.objects.all()
        user = request.user
        user_data = {}
        try:
            if user.user_type == 2:
                user_data = {
                    'role':'manager',
                    'name':user.username,
                    'user':user
                }
            elif user.user_type == 3:
                user_data = {
                    'role':'specialist',
                    'name':user.username,
                    'user':user
                }
            notifications = Notifications.objects.filter(user=request.user)[:5]
            seen = Notifications.objects.filter(user=request.user,seen=False)
            count = seen.count()
            if response.context_data:
                response.context_data['warehouses'] = warehouses
                response.context_data['w'] = int(self.warehouse)
                response.context_data['employee'] = user_data
                response.context_data['notifications'] = notifications
                response.context_data['ncount'] = count
                seen.update(seen=True)

            else:
                response.context_data = {'warehouses':warehouses, 'employee':user_data, 'notifications':notifications, 'ncount':count}

        except AttributeError:
            pass

        return response

