from datetime import date
from decimal import Decimal
from django.db.models import Sum
from expenses.models import Expense
from .models import ProjectMeta

def compute_project_metrics():
    meta = ProjectMeta.objects.first()
    if not meta:
        return None

    # Total Spent Overall
    total_spent_data = Expense.objects.aggregate(total=Sum('amount'))['total']
    total_spent = Decimal(total_spent_data) if total_spent_data else Decimal('0.00')

    today = date.today()
    start_date = meta.start_date
    target_end_date = meta.target_end_date
    total_budget = meta.total_budget

    elapsed_days = (today - start_date).days
    total_days = (target_end_date - start_date).days
    remaining_days = (target_end_date - today).days

    # Zero-day handling constraint
    if elapsed_days <= 0:
        daily_burn = Decimal('0.00')
    else:
        daily_burn = total_spent / Decimal(elapsed_days)

    if total_days <= 0:
        total_days = 1 # Avoid bad inputs negating real spend

    # Normalized projection formula
    projected_total = daily_burn * Decimal(total_days)
    
    # Cap projection to current realistic minimum
    projected_total = max(projected_total, total_spent)

    # Budget Health Variance
    variance = projected_total - total_budget

    if variance > Decimal('0.00'):
        status = "Over Budget"
    elif variance < Decimal('0.00'):
        status = "Under Budget"
    else:
        status = "On Track"

    # UI High-value additions
    monthly_burn = daily_burn * Decimal('30')

    # Category burn leaks
    category_contributions = Expense.objects.values('category__name') \
        .annotate(total=Sum('amount')) \
        .exclude(category__name__isnull=True) \
        .order_by('-total')

    # Labor vs material mapping across entire timeline
    labor_total_data = Expense.objects.filter(category__name="Labor").aggregate(total=Sum('amount'))['total']
    labor_spent = Decimal(labor_total_data) if labor_total_data else Decimal('0.00')
    material_spent = total_spent - labor_spent

    return {
        'meta': meta,
        'total_spent': total_spent,
        'daily_burn': daily_burn,
        'monthly_burn': monthly_burn,
        'projected_total': projected_total,
        'remaining_budget': total_budget - total_spent,
        'variance': variance,
        'status': status,
        'elapsed_days': elapsed_days,
        'total_days': total_days,
        'remaining_days': remaining_days,
        'percent_used': min(int((total_spent / total_budget) * 100), 100) if total_budget > 0 else 0,
        'category_contributions': category_contributions,
        'labor_spent': labor_spent,
        'material_spent': material_spent
    }
