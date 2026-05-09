from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
	list_display = ('name', 'contact', 'created_at')
	search_fields = ('name', 'contact')
	readonly_fields = ('created_at',)
