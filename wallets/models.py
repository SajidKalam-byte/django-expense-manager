from django.db import models
from django.db.models import Sum

class Wallet(models.Model):
    name = models.CharField(max_length=255)
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    @property
    def current_balance(self):
        credits = self.transactions.filter(transaction_type='CREDIT').aggregate(Sum('amount'))['amount__sum'] or 0
        debits = self.transactions.filter(transaction_type='DEBIT').aggregate(Sum('amount'))['amount__sum'] or 0
        return self.initial_balance + credits - debits

    def __str__(self):
        return f"{self.name} (Balance: ₹{self.current_balance})"

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    expense = models.ForeignKey('expenses.Expense', on_delete=models.CASCADE, null=True, blank=True, related_name='wallet_transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['wallet']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} on {self.wallet.name}"
