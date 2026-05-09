import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Wallet, WalletTransaction
from expenses.models import Expense

logger = logging.getLogger(__name__)

ALLOW_NEGATIVE_BALANCE = False

def check_balance_and_lock(wallet_id, amount_needed):
    wallet = Wallet.objects.select_for_update().get(id=wallet_id)
    if not ALLOW_NEGATIVE_BALANCE:
        if wallet.current_balance < amount_needed:
            logger.warning(f"Insufficient balance in wallet {wallet.name} for deduction of {amount_needed}")
            raise ValidationError(f"Insufficient balance in {wallet.name}")
    return wallet

def create_expense_transaction(expense: Expense):
    """
    Creates the appropriate WalletTransaction when an expense is created.
    """
    with transaction.atomic():
        wallet = check_balance_and_lock(expense.wallet_id, expense.amount)
        
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=expense.amount,
            transaction_type='DEBIT',
            expense=expense
        )
        logger.info(f"Created DEBIT transaction of {expense.amount} for expense {expense.id} on wallet {wallet.name}")


def create_expense_transactions_for_expense(expense: Expense):
    payments = list(expense.payments.all())

    if not payments:
        create_expense_transaction(expense)
        return

    with transaction.atomic():
        for payment in payments:
            wallet = check_balance_and_lock(payment.wallet_id, payment.amount)
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=payment.amount,
                transaction_type='DEBIT',
                expense=expense
            )
            logger.info(
                f"Created DEBIT transaction of {payment.amount} for expense {expense.id} on wallet {wallet.name}"
            )


def replace_expense_transactions_for_expense(expense: Expense):
    with transaction.atomic():
        WalletTransaction.objects.filter(expense=expense).delete()
        create_expense_transactions_for_expense(expense)

def update_expense_transaction(expense: Expense, old_wallet: Wallet, old_amount):
    """
    Handles wallet transaction updates safely when an expense is modified.
    If wallet remains the same, updates amount delta or recreates.
    If wallet changes, refunds old wallet and debits new wallet.
    """
    with transaction.atomic():
        if old_wallet == expense.wallet:
            delta = expense.amount - old_amount
            if delta != 0:
                wallet = check_balance_and_lock(expense.wallet_id, delta if delta > 0 else 0)
                
                if delta > 0:
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=delta,
                        transaction_type='DEBIT',
                        expense=expense
                    )
                    logger.info(f"Updated expense {expense.id}: Extra DEBIT {delta} on wallet {wallet.name}")
                else:
                    WalletTransaction.objects.create(
                        wallet=wallet,
                        amount=abs(delta),
                        transaction_type='CREDIT',
                        expense=expense
                    )
                    logger.info(f"Updated expense {expense.id}: Partial CREDIT {abs(delta)} on wallet {wallet.name}")
        else:
            old_w_locked = Wallet.objects.select_for_update().get(id=old_wallet.id)
            WalletTransaction.objects.create(
                wallet=old_w_locked,
                amount=old_amount,
                transaction_type='CREDIT',
                expense=expense
            )
            logger.info(f"Updated expense {expense.id}: Full CREDIT {old_amount} on OLD wallet {old_w_locked.name}")
            
            new_w_locked = check_balance_and_lock(expense.wallet_id, expense.amount)
            WalletTransaction.objects.create(
                wallet=new_w_locked,
                amount=expense.amount,
                transaction_type='DEBIT',
                expense=expense
            )
            logger.info(f"Updated expense {expense.id}: Full DEBIT {expense.amount} on NEW wallet {new_w_locked.name}")

def delete_expense_transaction(expense: Expense):
    """
    Reverses the expense impact before it is deleted.
    Since WalletTransaction cascades, deleting the expense deletes the ledger entries natively.
    """
    with transaction.atomic():
        payments = list(expense.payments.all())
        if payments:
            for payment in payments:
                Wallet.objects.select_for_update().get(id=payment.wallet_id)
                logger.info(
                    f"Deleting expense {expense.id}. Linked transactions will cascade delete, refunding {payment.wallet.name}."
                )
            return

        wallet = Wallet.objects.select_for_update().get(id=expense.wallet_id)
        logger.info(f"Deleting expense {expense.id}. Linked transactions will cascade delete, refunding {wallet.name}.")
