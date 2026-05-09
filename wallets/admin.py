from django.contrib import admin
from .models import Wallet, WalletTransaction

class WalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'initial_balance', 'current_balance')
    search_fields = ('name',)

class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'expense', 'created_at')
    list_filter = ('transaction_type', 'wallet', 'created_at')
    readonly_fields = ('created_at',)

admin.site.register(Wallet, WalletAdmin)
admin.site.register(WalletTransaction, WalletTransactionAdmin)
