from django.db import models

class IndustryCycle(models.Model):
    industry_name = models.CharField(max_length=100)
    cycle_category = models.CharField(max_length=20, choices=[('Expansion', 'Expansion'), ('Peak', 'Peak'), ('Recession', 'Recession'), ('Trough', 'Trough'), ('Recovery', 'Recovery')])
    year = models.IntegerField()
