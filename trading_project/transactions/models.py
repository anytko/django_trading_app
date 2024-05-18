from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10)  # 'BUY' or 'SELL'
    stock_symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)