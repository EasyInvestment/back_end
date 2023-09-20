# cycles/views.py

from django.shortcuts import render
from .models import IndustryCycle

def industry_cycles_view(request):
    data = IndustryCycle.objects.all()
    return render(request, 'cycle.html', {'data': data})
