from django.urls import path
from .views import InventoryUpdateView, WalletUpdateView, ActorWalletView, ActorInventoryView, ActorFrozenWalletView, \
    ActorFrozenInventoryView, FreezeInventoryView, UnfreezeInventoryView, FreezeWalletView, UnfreezeWalletView

urlpatterns = [
    # Существующие
    path('inventory/update/', InventoryUpdateView.as_view()),
    path('wallet/update/', WalletUpdateView.as_view()),
    path('actor/<int:actor_id>/inventory/', ActorInventoryView.as_view()),
    path('actor/<int:actor_id>/wallet/', ActorWalletView.as_view()),

    # Новые — просмотр замороженных активов
    path('actor/<int:actor_id>/frozen_inventory/', ActorFrozenInventoryView.as_view(), name='actor-frozen-inventory'),
    path('actor/<int:actor_id>/frozen_wallet/', ActorFrozenWalletView.as_view(), name='actor-frozen-wallet'),

    # Internal freeze/unfreeze (уже есть)
    path('inventory/freeze/', FreezeInventoryView.as_view()),
    path('inventory/unfreeze/', UnfreezeInventoryView.as_view()),
    path('wallet/freeze/', FreezeWalletView.as_view()),
    path('wallet/unfreeze/', UnfreezeWalletView.as_view()),
]