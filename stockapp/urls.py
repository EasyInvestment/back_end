from django.urls import path
from .views import stock_monitor

urlpatterns = [
    path('monitor/', stock_monitor, name='stock_monitor'),
]
