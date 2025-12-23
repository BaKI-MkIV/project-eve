from django.urls import path, include
from rest_framework.routers import DefaultRouter

from products.views import ProductViewSet
from .views import CurrencyViewSet, TagViewSet, MarketLotViewSet, TransferViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'market/lots', MarketLotViewSet, basename='market-lot')
router.register(r'transfers', TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]
