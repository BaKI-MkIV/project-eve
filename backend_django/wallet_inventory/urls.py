from django.urls import path
from .views import InventoryUpdateView, WalletUpdateView

urlpatterns = [
    path('inventory/update/', InventoryUpdateView.as_view(), name='inventory-update'),
    path('wallet/update/', WalletUpdateView.as_view(), name='wallet-update'),
]