from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet
from actors.views import ActorViewSet
from products.views import ProductViewSet
from inventory.views import InventoryItemViewSet
from economy.views import CurrencyViewSet, ActorBalanceViewSet
from market.views import MarketOrderViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'actors', ActorViewSet)
router.register(r'products', ProductViewSet)
router.register(r'inventory', InventoryItemViewSet)
router.register(r'currencies', CurrencyViewSet)
router.register(r'balances', ActorBalanceViewSet)
router.register(r'market-orders', MarketOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
