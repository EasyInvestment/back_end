# views.py (recommandation_app/views.py 파일 내)
from django.shortcuts import redirect, render
from .forms import UserInputForm
from .main import main  # main 함수를 임포트합니다.

def input_view(request):
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            # 필요한 경우 여기에 사용자 입력 처리 로직을 추가
            return redirect('output')
    else:
        form = UserInputForm()
    return render(request, 'input.html', {'form': form})

def output_view(request):
    # main 함수에서 추천 카테고리 리스트를 받습니다.
    recommended_categories = main()

    # 이 리스트를 템플릿에 전달합니다.
    context = {'recommended_categories': recommended_categories}
    return render(request, 'output.html', context)
