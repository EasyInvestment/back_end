from django.shortcuts import redirect, render
from .forms import UserInputForm

def input_view(request):
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            # 입력을 처리하고 분석하는 로직을 추가하세요.
            # 추천 종목을 계산하고 결과를 저장합니다.
            # 이후 결과를 출력하는 페이지로 리다이렉션합니다.
            return redirect('output')
    else:
        form = UserInputForm()

    return render(request, 'input.html', {'form': form})

def output_view(request):
    # 분석된 결과를 표시하는 뷰입니다.
    # 결과를 템플릿에 전달하여 사용자에게 보여줍니다.
    return render(request, 'output.html')
