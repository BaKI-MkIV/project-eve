from django.urls import path
from .views import InventoryUpdateView, WalletUpdateView, ActorWalletView, ActorInventoryView, ActorFrozenWalletView, \
    ActorFrozenInventoryView

urlpatterns = [
    path('inventory/update/', InventoryUpdateView.as_view(), name='inventory-update'),
    path('wallet/update/', WalletUpdateView.as_view(), name='wallet-update'),

    path('actor/<int:actor_id>/inventory/', ActorInventoryView.as_view(), name='actor-inventory'),
    path('actor/<int:actor_id>/wallet/', ActorWalletView.as_view(), name='actor-wallet'),


    path('actor/<int:actor_id>/frozen_wallet/', ActorFrozenWalletView.as_view(), name='actor-frozen-wallet'),
    path('actor/<int:actor_id>/frozen_inventory/', ActorFrozenInventoryView.as_view(), name='actor-frozen-inventory'),
]