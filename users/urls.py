from django.urls import path
from . import views

app_name = 'users' # 앱 네임스페이스 설정

urlpatterns = [
  path('login/', views.login_view, name="login"),
  path("logout", views.logout_view, name="logout"),
  path('signup/', views.signup_view, name='signup'),
]