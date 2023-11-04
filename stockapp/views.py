from rest_framework.decorators import api_view
from rest_framework.response import Response
from .monitor import monitor

@api_view(['GET'])
def stock_monitor(request):
    if request.method == 'GET':
        result = monitor()
        # 데이터 프레임에서 처음 100개의 로우만 선택
        limited_result = result.head(100)
        print(limited_result)
        # 선택된 로우들을 딕셔너리 리스트로 변환하여 JSON 응답으로 보냄
        return Response({'data': limited_result.to_dict(orient='records')})
