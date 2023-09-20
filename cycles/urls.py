# cycles/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('industry_cycles/', views.industry_cycles_view, name='industry_cycles'),
]
