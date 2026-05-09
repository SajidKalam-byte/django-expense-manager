from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Wallet

class WalletListView(ListView):
    model = Wallet
    template_name = 'wallets/wallet_list.html'
    context_object_name = 'wallets'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_balance'] = sum(wallet.current_balance for wallet in context['wallets'])
        return context

class WalletDetailView(DetailView):
    model = Wallet
    template_name = 'wallets/wallet_detail.html'
    context_object_name = 'wallet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.all().order_by('-created_at')
        return context

def audit_wallet(request, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id)

    total = wallet.transactions.aggregate(
        debit=Coalesce(Sum('amount', filter=Q(transaction_type='DEBIT')), Decimal('0.00')),
        credit=Coalesce(Sum('amount', filter=Q(transaction_type='CREDIT')), Decimal('0.00'))
    )

    return JsonResponse({
        'wallet_id': wallet.id,
        'wallet_name': wallet.name,
        'initial_balance': float(wallet.initial_balance),
        'total_debit': float(total['debit']),
        'total_credit': float(total['credit']),
        'calculated_balance': float(wallet.initial_balance) + float(total['credit']) - float(total['debit'])
    })
