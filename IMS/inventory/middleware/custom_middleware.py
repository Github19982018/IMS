from inventory.models import Warehouse

class Warehouse_middleware:
    warehouse = 1
    def __init__(self,get_response): 
        self.get_response = get_response
    def __call__(self, request):
        self.warehouse = request.GET.get('warehouse') or self.warehouse
        request.w = self.warehouse
        response = self.get_response(request)
        return response
    
    def process_template_response(self,request, response):
        warehouses = Warehouse.objects.all()
        response.context_data['warehouses'] = warehouses
        response.context_data['w'] = self.warehouse
        return response
