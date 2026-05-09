import os
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from core.models import ProjectMeta
from core.services import compute_project_metrics
from expenses.models import Expense, Category
from wallets.models import Wallet

def run_test():
    print("--- Phase 4: Analytics Math Verification ---")

    # Cleanup previous meta
    ProjectMeta.objects.all().delete()
    
    # Setup test data
    wallet, _ = Wallet.objects.get_or_create(name="Test Wallet")
    category, _ = Category.objects.get_or_create(name="Material")
    
    today = date.today()
    start_date = today - timedelta(days=10)
    target_end_date = today + timedelta(days=10)
    total_budget = Decimal('10000.00')
    
    meta = ProjectMeta.objects.create(
        total_budget=total_budget,
        start_date=start_date,
        target_end_date=target_end_date
    )
    
    # 1. Test Day 10 Spend (Total 1000, 10 days elapsed -> 100/day)
    Expense.objects.create(title="Test 1", amount=Decimal('1000.00'), wallet=wallet, category=category, date=today)
    
    metrics = compute_project_metrics()
    
    print(f"Elapsed Days: {metrics['elapsed_days']}")
    print(f"Daily Burn: {metrics['daily_burn']}")
    print(f"Projected Total: {metrics['projected_total']}")
    print(f"Status: {metrics['status']}")
    
    # Assertions
    assert metrics['elapsed_days'] == 10
    assert metrics['daily_burn'] == Decimal('100.00')
    # total_days = (target - start) = 20 days. 
    # projected = daily_burn * total_days = 100 * 20 = 2000.
    assert metrics['projected_total'] == Decimal('2000.00')
    assert metrics['status'] == "Under Budget" # 2000 < 10000
    
    # 2. Test Over Budget
    meta.total_budget = Decimal('1500.00')
    meta.save()
    metrics = compute_project_metrics()
    assert metrics['status'] == "Over Budget"
    
    print("--- Tests Passed Successfully ---")

if __name__ == "__main__":
    run_test()
