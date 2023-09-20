# cycles/management/commands/create_dummy_data.py
from django.core.management.base import BaseCommand
from cycles.models import IndustryCycle
import random

class Command(BaseCommand):
    help = 'Create dummy data for industry cycles'

    def handle(self, *args, **kwargs):
        industries = ['Industry 1', 'Industry 2', 'Industry 3', 'Industry 4', 'Industry 5']
        years = list(range(2020, 2030))
        categories = ['Expansion', 'Peak', 'Recession', 'Trough', 'Recovery']

        for industry in industries:
            for year in years:
                cycle_category = random.choice(categories)
                IndustryCycle.objects.create(industry_name=industry, cycle_category=cycle_category, year=year)
                
        self.stdout.write(self.style.SUCCESS('Dummy data created successfully'))