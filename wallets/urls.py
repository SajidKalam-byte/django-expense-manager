from django.urls import path
from . import views

app_name = 'wallets'

urlpatterns = [
    path('', views.WalletListView.as_view(), name='list'),
    path('<int:pk>/', views.WalletDetailView.as_view(), name='detail'),
    path('<int:wallet_id>/audit/', views.audit_wallet, name='audit'),
]
