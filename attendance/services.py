from decimal import Decimal
from django.db import transaction
from expenses.models import Expense, Category
from wallets.services import create_expense_transaction, update_expense_transaction, delete_expense_transaction
from .models import Attendance

def get_or_create_labor_category():
    # Helper to enforce Labor category existence
    cat, created = Category.objects.get_or_create(name="Labor")
    return cat

@transaction.atomic
def create_attendance(data):
    # Enforce wage rule
    if data.get('work_type'):
        data['wage_per_worker'] = data['work_type'].default_wage

    multiplier = Decimal('0.5') if data.get('is_half_day', False) else Decimal('1.0')
    total_amount = (
        Decimal(data['workers_count']) *
        Decimal(data['wage_per_worker']) *
        multiplier
    )
    
    # Optional performance cache
    data['total_amount'] = total_amount

    attendance = Attendance.objects.create(**data)

    labor_category = get_or_create_labor_category()
    title_suffix = attendance.work_type.name if attendance.work_type else attendance.custom_work_note[:20]
    
    # 1. Create linked expense
    expense = Expense.objects.create(
        title=f"Labor - {title_suffix}",
        amount=total_amount,
        category=labor_category,
        wallet=attendance.wallet,
        date=attendance.date,
        notes=attendance.custom_work_note,
        phase=attendance.phase,
        is_system_generated=True  # Important security constraint
    )

    # 2. Trigger wallet ledger integration
    create_expense_transaction(expense)

    # 3. Securely link
    attendance.linked_expense = expense
    attendance.save(update_fields=['linked_expense'])

    return attendance

@transaction.atomic
def update_attendance(attendance, new_data):
    # Capture OLD expense data BEFORE ANY MUTATION
    old_expense = attendance.linked_expense
    old_wallet = old_expense.wallet
    old_amount = old_expense.amount

    # Enforce wage rule
    if new_data.get('work_type'):
        new_data['wage_per_worker'] = new_data['work_type'].default_wage

    for key, value in new_data.items():
        setattr(attendance, key, value)

    multiplier = Decimal('0.5') if attendance.is_half_day else Decimal('1.0')
    new_amount = (
        Decimal(attendance.workers_count) *
        Decimal(attendance.wage_per_worker) *
        multiplier
    )
    attendance.total_amount = new_amount
    attendance.save()

    # Apply properties to linked expense
    title_suffix = attendance.work_type.name if attendance.work_type else attendance.custom_work_note[:20]
    old_expense.title = f"Labor - {title_suffix}"
    old_expense.amount = new_amount
    old_expense.date = attendance.date
    old_expense.notes = attendance.custom_work_note
    old_expense.phase = attendance.phase
    old_expense.wallet = attendance.wallet
    old_expense.save()

    # Pass the perfectly captured old ledger footprint to strictly accurate delta logic
    update_expense_transaction(old_expense, old_wallet, old_amount)

    return attendance

@transaction.atomic
def delete_attendance(attendance):
    expense = attendance.linked_expense

    if expense:
        # Reverses the wallet impact via DEBIT -> CREDIT refunds
        delete_expense_transaction(expense)
        
        # Nullify the protected foreign key first
        attendance.linked_expense = None
        attendance.save(update_fields=['linked_expense'])
        
        expense.delete()  # WalletTransactions cascade delete cleanly!

    attendance.delete()
