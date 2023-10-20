from rest_framework.decorators import api_view
from rest_framework.response import Response
from .monitor import monitor

@api_view(['GET'])
def stock_monitor(request):
    if request.method == 'GET':
        result = monitor()
        print(result)
        return Response({'data': result.to_dict(orient='records')})
