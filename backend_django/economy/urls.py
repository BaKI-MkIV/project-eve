from django.urls import path, include
from rest_framework.routers import DefaultRouter

from products.views import ProductViewSet
from .views import CurrencyViewSet, TagViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]
