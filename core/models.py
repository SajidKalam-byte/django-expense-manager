from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError

class ProjectMeta(models.Model):
    total_budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateField()
    target_end_date = models.DateField()

    class Meta:
        verbose_name_plural = "Project Meta"

    def save(self, *args, **kwargs):
        if not self.pk and ProjectMeta.objects.exists():
            raise ValidationError('There can be only one ProjectMeta instance')
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Project Global Budget: ₹{self.total_budget}"
