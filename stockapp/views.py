from django.http import JsonResponse
from .monitor import monitor

def stock_monitor(request):
    result = monitor()
    print(result)
    
    return JsonResponse({'data': result.to_dict(orient='records')})
