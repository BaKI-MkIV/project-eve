
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from market.views import MarketOrderViewSet
from products.views import ProductViewSet
from actors.views import ActorViewSet
from accounts.views import UserViewSet
from transfers.views import TransferRequestViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'actors', ActorViewSet, basename='actor')
router.register(r'users', UserViewSet, basename='user')  # ← Добавь эту строку
router.register(r'transfer-requests', TransferRequestViewSet, basename='transfer_request')
router.register(r'market/orders', MarketOrderViewSet, basename='market_order')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('', include(router.urls)),  # или path('api/', include(router.urls))
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]