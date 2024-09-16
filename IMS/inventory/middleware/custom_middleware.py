from inventory.models import Warehouse

class Warehouse_middleware:
    with open('data/warehouse.txt','+w') as wfile:
        wfile.write('1')

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
    
    def process_template_response(self,request, response):
        warehouses = Warehouse.objects.all()
        user = request.user
        user_data = {}
        if user.user_type == 2:
            user_data = {
                'role':'manager',
                'name':user.username
            }
        elif user.user_type == 3:
            user_data = {
                'role':'specialist',
                'name':user.username
            }

        if response.context_data:
            response.context_data['warehouses'] = warehouses
            response.context_data['w'] = int(self.warehouse)
            response.context_data['user'] = user_data

        return response

