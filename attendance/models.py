from django.db import models

class WorkType(models.Model):
    name = models.CharField(max_length=100)
    default_wage = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} (₹{self.default_wage})"


class Attendance(models.Model):
    date = models.DateField(db_index=True)
    workers_count = models.PositiveIntegerField()

    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    custom_work_note = models.CharField(max_length=255, blank=True)
    wage_per_worker = models.DecimalField(max_digits=10, decimal_places=2)
    is_half_day = models.BooleanField(default=False)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Note: Using CharField here to match the expenses.phase schema in Phase 2
    phase = models.CharField(max_length=100, blank=True, null=True)

    wallet = models.ForeignKey(
        'wallets.Wallet',
        on_delete=models.PROTECT
    )

    linked_expense = models.OneToOneField(
        'expenses.Expense',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Attendance {self.date} - {self.workers_count} workers"
