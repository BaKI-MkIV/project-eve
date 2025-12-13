from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from products.views import ProductViewSet
from actors.views import ActorViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'actors', ActorViewSet, basename='actor')

urlpatterns = [
    path('admin/', admin.site.urls),

    # accounts — обычные path()
    path('auth/', include('accounts.urls')),

    # API на ViewSet'ах
    path('', include(router.urls)),
]
