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
        user = request.user
        response = self.get_response(request)
        return response
    
    def process_template_response(self,request, response):
        warehouses = Warehouse.objects.all()
        response.context_data['warehouses'] = warehouses
        response.context_data['w'] = int(self.warehouse)
        return response

