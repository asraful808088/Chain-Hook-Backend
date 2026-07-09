from django.urls import path
from .views import (
    WalletView, TransactionListView, ConvertCurrencyView,
    CurrencyPriceHistoryView, WalletAnalyticsView,
    TransferView, PaymentView
)

urlpatterns = [
    path('', WalletView.as_view(), name='wallet-detail'),
    path('transactions/', TransactionListView.as_view(), name='wallet-transactions'),
    path('convert/', ConvertCurrencyView.as_view(), name='wallet-convert'),
    path('transfer/', TransferView.as_view(), name='wallet-transfer'),
    path('payment/', PaymentView.as_view(), name='wallet-payment'),
    path('price-history/', CurrencyPriceHistoryView.as_view(), name='wallet-price-history'),
    path('analytics/', WalletAnalyticsView.as_view(), name='wallet-analytics'),
]
