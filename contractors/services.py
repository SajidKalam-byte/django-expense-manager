from decimal import Decimal
from django.db import transaction
from expenses.models import Expense, Category
from wallets.services import create_expense_transaction, update_expense_transaction, delete_expense_transaction
from .models import ContractorPayment


def get_or_create_contractor_category():
    category, created = Category.objects.get_or_create(name="Contractor")
    return category


@transaction.atomic
def create_contractor_payment(data):
    payment = ContractorPayment.objects.create(**data)

    contractor_category = get_or_create_contractor_category()
    expense = Expense.objects.create(
        title=f"Contractor - {payment.contractor.name}",
        amount=payment.amount,
        category=contractor_category,
        wallet=payment.wallet,
        date=payment.date,
        notes=payment.reason,
        phase=payment.phase,
        is_system_generated=True,
    )

    create_expense_transaction(expense)

    payment.linked_expense = expense
    payment.save(update_fields=['linked_expense'])

    return payment


@transaction.atomic
def update_contractor_payment(payment, new_data):
    old_expense = payment.linked_expense
    old_wallet = old_expense.wallet
    old_amount = old_expense.amount

    for key, value in new_data.items():
        setattr(payment, key, value)

    payment.save()

    old_expense.title = f"Contractor - {payment.contractor.name}"
    old_expense.amount = payment.amount
    old_expense.date = payment.date
    old_expense.notes = payment.reason
    old_expense.phase = payment.phase
    old_expense.wallet = payment.wallet
    old_expense.save()

    update_expense_transaction(old_expense, old_wallet, old_amount)

    return payment


@transaction.atomic
def delete_contractor_payment(payment):
    expense = payment.linked_expense

    if expense:
        delete_expense_transaction(expense)
        payment.linked_expense = None
        payment.save(update_fields=['linked_expense'])
        expense.delete()

    payment.delete()
