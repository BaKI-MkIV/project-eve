# eve_backend/urls.py (добавь импорт и регистрацию)

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from products.views import ProductViewSet
from actors.views import ActorViewSet
from accounts.views import UserViewSet  # ← Добавь импорт

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'actors', ActorViewSet, basename='actor')
router.register(r'users', UserViewSet, basename='user')  # ← Добавь эту строку

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('', include(router.urls)),  # или path('api/', include(router.urls))
]