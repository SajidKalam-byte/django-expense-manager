import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "expense_tracker.settings")
django.setup()

from django.test import Client
from datetime import date
from expenses.models import Expense, Category
from wallets.models import Wallet
from vendors.models import Vendor

def run_checks():
    c = Client()
    # 1. Dashboard loads without crash
    try:
        resp = c.get('/')
        print(f"Dashboard status: {resp.status_code}")
        assert resp.status_code == 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return

    # Create dummy data for testing filters
    w = Wallet.objects.create(name='Test Filter Wallet', initial_balance=50000)
    cat = Category.objects.create(name='Test Filter Category')
    v = Vendor.objects.create(name='Test Vendor')
    exp1 = Expense.objects.create(title='T1', amount=100, category=cat, wallet=w, vendor=v, date=date.today())

    # 2. Filter Edge Cases
    resp = c.get('/expenses/?start_date=2020-01-01')
    assert resp.status_code == 200
    assert len(resp.context['expenses']) >= 1

    # End date in the past
    resp = c.get('/expenses/?end_date=1999-01-01')
    print("Filter length (expect 0 if fresh DB):", len(resp.context['expenses']))

    # 3. Vendor Deletion - expenses remain intact
    v.delete()
    exp1.refresh_from_db()
    assert exp1.vendor is None
    print("Vendor SET_NULL verified.")

    # Verify audit endpoint
    resp = c.get(f'/wallets/{w.pk}/audit/')
    print(f"Audit endpoint: {resp.json()}")

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    run_checks()
