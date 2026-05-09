import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from wallets.models import Wallet, WalletTransaction
from expenses.models import Expense, Category
from datetime import date
from wallets.services import create_expense_transaction, update_expense_transaction, delete_expense_transaction


def run_wallet_checks():
    # Clear in safe order to avoid RESTRICT errors
    Expense.objects.all().delete()
    Wallet.objects.all().delete()
    Category.objects.all().delete()
    WalletTransaction.objects.all().delete()

    w = Wallet.objects.create(name="Cash Wallet", initial_balance=50000)
    c = Category.objects.create(name="Construction")

    print("Initial Balance:", w.current_balance)

    e = Expense.objects.create(title="Bricks", amount=10000, category=c, wallet=w, date=date.today())
    create_expense_transaction(e)
    print("After Expense Create (10000):", w.current_balance)

    old_amt = e.amount
    e.amount = 12000
    e.save()
    update_expense_transaction(e, w, old_amt)
    print("After Update (increased to 12000):", w.current_balance)

    old_amt = e.amount
    e.amount = 9000
    e.save()
    update_expense_transaction(e, w, old_amt)
    print("After Update (decreased to 9000):", w.current_balance)

    delete_expense_transaction(e)
    e.delete()
    print("After Delete:", w.current_balance)
    print("Transactions count:", w.transactions.count())
    for tx in w.transactions.all().order_by('created_at'):
        print(f" - {tx}")


if __name__ == "__main__":
    run_wallet_checks()
