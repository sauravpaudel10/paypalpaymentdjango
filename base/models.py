
# Create your models here.
# models.py

from django.db import models
from django.contrib.auth.models import User


class Transaction(models.Model):
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=255)
    payment_date = models.DateTimeField(null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    paid  = models.BooleanField(default=False)
    paypal_plan_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"MyTransaction - {self.invoice_number}"



