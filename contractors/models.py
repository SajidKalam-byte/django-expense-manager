from django.db import models


class Contractor(models.Model):
	name = models.CharField(max_length=255)
	contact = models.CharField(max_length=255, blank=True)

	def __str__(self):
		return self.name


class ContractorPayment(models.Model):
	contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='payments')
	date = models.DateField()
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	wallet = models.ForeignKey('wallets.Wallet', on_delete=models.PROTECT)
	reason = models.CharField(max_length=255, blank=True)
	phase = models.CharField(max_length=100, blank=True, null=True)
	linked_expense = models.OneToOneField('expenses.Expense', on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=['date']),
			models.Index(fields=['contractor']),
		]

	def __str__(self):
		return f"{self.contractor.name} - ₹{self.amount}"
