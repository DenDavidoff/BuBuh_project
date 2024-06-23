from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Record(models.Model):
    CATEGORY_CHOICES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=7, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount}"