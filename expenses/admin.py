from django.contrib import admin
from .models import Category, Expense, ExpensePayment, ExpenseItem

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'category', 'wallet', 'payment_mode', 'date', 'created_at')
    list_filter = ('category', 'wallet', 'payment_mode', 'date')
    search_fields = ('title', 'subcategory', 'invoice_number', 'notes')
    readonly_fields = ('created_at',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Expense, ExpenseAdmin)


@admin.register(ExpensePayment)
class ExpensePaymentAdmin(admin.ModelAdmin):
    list_display = ('expense', 'wallet', 'amount')
    list_filter = ('wallet',)


@admin.register(ExpenseItem)
class ExpenseItemAdmin(admin.ModelAdmin):
    list_display = ('expense', 'name', 'amount', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
