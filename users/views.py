from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .models import User
from django.contrib import messages
# Create your views here.


def login_view(request):
  if request.method == "POST":
    id = request.POST["id"]
    pw = request.POST["pw"]
    user = authenticate(username=id, password=pw)
    if user is not None:
      print("인증성공")
      login(request, user)
    else:
      print("인증실패")
  return render(request, "users/login.html")


def logout_view(request):
  logout(request)
  return redirect("user:login")


def signup_view(request):

  if request.method == "POST":
    name = request.POST["name"]
    phone = request.POST["phone"]
    pw = request.POST["pw"]
    pwc = request.POST["pwc"]

    if pw == pwc:
      user = User.objects.create_user(username=name, password=pw)
      user.phone = phone  # phone 필드에 값을 할당
      user.save()
      login(request, user)  # 회원가입 후 자동으로 로그인
      return redirect("user:login")
    else:
      messages.error(request, "비밀번호와 비밀번호 확인이 일치하지 않습니다.")

  return render(request, "users/signup.html")