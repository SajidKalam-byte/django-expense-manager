from django.db import models
from wallets.models import Wallet

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

class Expense(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=15, choices=[('expense', 'Expense'), ('refund', 'Refund')], default='expense')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT, related_name='expenses')
    subcategory = models.CharField(max_length=255, blank=True, null=True) # Optional text or could just use Category hierarchy
    wallet = models.ForeignKey(Wallet, on_delete=models.RESTRICT, related_name='expenses')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    payment_mode = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    phase = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='invoices/', blank=True, null=True)
    is_system_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['category']),
            models.Index(fields=['wallet']),
        ]

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.date})"


class ExpensePayment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='payments')
    wallet = models.ForeignKey('wallets.Wallet', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.expense.title} -> {self.wallet.name} (₹{self.amount})"


class ExpenseItem(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['expense']),
        ]

    def __str__(self):
        return f"{self.name} (₹{self.amount})"
