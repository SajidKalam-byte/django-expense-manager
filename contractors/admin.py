from django.contrib import admin
from .models import Contractor, ContractorPayment


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
	list_display = ('name', 'contact')
	search_fields = ('name', 'contact')


@admin.register(ContractorPayment)
class ContractorPaymentAdmin(admin.ModelAdmin):
	list_display = ('contractor', 'date', 'amount', 'wallet', 'phase')
	list_filter = ('date', 'wallet', 'phase')
	search_fields = ('contractor__name', 'reason')
	readonly_fields = ('created_at',)
