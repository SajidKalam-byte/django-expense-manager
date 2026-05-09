import os
import argparse
from datetime import date, timedelta
from decimal import Decimal

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from core.models import ProjectMeta
from wallets.models import Wallet, WalletTransaction
from wallets.services import create_expense_transaction
from vendors.models import Vendor
from expenses.models import Expense, Category
from attendance.models import WorkType, Attendance
from attendance.services import create_attendance


def reset_data():
    # Order matters due to PROTECT/RESTRICT constraints
    Attendance.objects.all().delete()
    Expense.objects.all().delete()
    WalletTransaction.objects.all().delete()
    Wallet.objects.all().delete()
    Category.objects.all().delete()
    Vendor.objects.all().delete()
    WorkType.objects.all().delete()
    ProjectMeta.objects.all().delete()


def seed_project_meta():
    return ProjectMeta.objects.create(
        total_budget=Decimal('2500000.00'),
        start_date=date.today() - timedelta(days=90),
        target_end_date=date.today() + timedelta(days=120),
    )


def seed_wallets():
    return [
        Wallet.objects.create(name='Cash Wallet', initial_balance=Decimal('500000.00')),
        Wallet.objects.create(name='Bank Wallet', initial_balance=Decimal('2000000.00')),
    ]


def seed_vendors():
    return [
        Vendor.objects.create(name='Sharma Traders', contact='9876543210'),
        Vendor.objects.create(name='City Steel Depot', contact='9123456780'),
        Vendor.objects.create(name='Rapid Electricals', contact='9988776655'),
    ]


def seed_categories():
    materials = Category.objects.create(name='Materials')
    labor = Category.objects.create(name='Labor')
    plumbing = Category.objects.create(name='Plumbing', parent=materials)
    electrical = Category.objects.create(name='Electrical', parent=materials)
    cement = Category.objects.create(name='Cement', parent=materials)
    tiles = Category.objects.create(name='Tiles', parent=materials)
    finishing = Category.objects.create(name='Finishing')

    return {
        'materials': materials,
        'labor': labor,
        'plumbing': plumbing,
        'electrical': electrical,
        'cement': cement,
        'tiles': tiles,
        'finishing': finishing,
    }


def seed_expenses(wallets, vendors, categories):
    expenses = [
        {
            'title': 'Cement Bags',
            'amount': Decimal('85000.00'),
            'category': categories['cement'],
            'wallet': wallets[1],
            'vendor': vendors[0],
            'payment_mode': 'UPI',
            'invoice_number': 'INV-1001',
            'date': date.today() - timedelta(days=60),
            'phase': 'Foundation',
            'notes': 'Cement purchase for base slab'
        },
        {
            'title': 'Plumbing Pipes',
            'amount': Decimal('42000.00'),
            'category': categories['plumbing'],
            'wallet': wallets[1],
            'vendor': vendors[0],
            'payment_mode': 'Bank Transfer',
            'invoice_number': 'INV-1002',
            'date': date.today() - timedelta(days=45),
            'phase': 'Plumbing',
            'notes': 'PVC and GI pipes'
        },
        {
            'title': 'Electrical Wiring',
            'amount': Decimal('56000.00'),
            'category': categories['electrical'],
            'wallet': wallets[1],
            'vendor': vendors[2],
            'payment_mode': 'Cash',
            'invoice_number': 'INV-1003',
            'date': date.today() - timedelta(days=30),
            'phase': 'Electrical',
            'notes': 'Cables and switches'
        },
        {
            'title': 'Tiles Purchase',
            'amount': Decimal('120000.00'),
            'category': categories['tiles'],
            'wallet': wallets[1],
            'vendor': vendors[1],
            'payment_mode': 'UPI',
            'invoice_number': 'INV-1004',
            'date': date.today() - timedelta(days=15),
            'phase': 'Finishing',
            'notes': 'Floor tiles for living area'
        },
        {
            'title': 'Paint and Finishing',
            'amount': Decimal('38000.00'),
            'category': categories['finishing'],
            'wallet': wallets[0],
            'vendor': vendors[0],
            'payment_mode': 'Cash',
            'invoice_number': 'INV-1005',
            'date': date.today() - timedelta(days=7),
            'phase': 'Finishing',
            'notes': 'Interior paint materials'
        },
    ]

    created = []
    for data in expenses:
        expense = Expense.objects.create(
            title=data['title'],
            amount=data['amount'],
            category=data['category'],
            wallet=data['wallet'],
            vendor=data['vendor'],
            payment_mode=data['payment_mode'],
            invoice_number=data['invoice_number'],
            date=data['date'],
            phase=data['phase'],
            notes=data['notes'],
        )
        create_expense_transaction(expense)
        created.append(expense)

    return created


def seed_attendance(wallets):
    mason = WorkType.objects.create(name='Mason', default_wage=Decimal('900.00'))
    painter = WorkType.objects.create(name='Painter', default_wage=Decimal('800.00'))

    entries = [
        {
            'date': date.today() - timedelta(days=20),
            'workers_count': 6,
            'work_type': mason,
            'is_half_day': False,
            'wallet': wallets[0],
            'phase': 'Foundation',
            'custom_work_note': 'Foundation block work'
        },
        {
            'date': date.today() - timedelta(days=10),
            'workers_count': 4,
            'work_type': painter,
            'is_half_day': True,
            'wallet': wallets[0],
            'phase': 'Finishing',
            'custom_work_note': 'Primer coat'
        },
    ]

    created = []
    for data in entries:
        created.append(create_attendance(data))

    return created


def main():
    parser = argparse.ArgumentParser(description='Seed dummy data for Homee')
    parser.add_argument('--reset', action='store_true', help='Clear existing data before seeding')
    args = parser.parse_args()

    if args.reset:
        reset_data()

    seed_project_meta()
    wallets = seed_wallets()
    vendors = seed_vendors()
    categories = seed_categories()
    seed_expenses(wallets, vendors, categories)
    seed_attendance(wallets)

    print('Seed completed successfully.')


if __name__ == '__main__':
    main()
