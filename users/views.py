from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from .models import User
# Create your views here.


def login_view(request):
  if request.method == "POST":
    id = request.request.POST["id"]
    pw = request.request.POST["pw"]
    user = authenticate(id=id, pw=pw)
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
    print(request.POST)
    name = request.POST["name"]
    phone = request.POST["phone"]
    pw = request.POST["pw"]
    pwc = request.POST["pwc"]

    user = User.object.create_user(name, phone, pw)
    user.pwc = pwc
    user.save()

    return redirect("user:login")
  return render(request, "users/signup.html")