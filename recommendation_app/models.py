from django.db import models

class UserInput(models.Model):
    period = models.CharField(max_length=20)
    risk = models.CharField(max_length=20)
    goal = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.period} - {self.risk}"