from django.urls import path, include
from rest_framework.routers import DefaultRouter

from actors.views import ActorViewSet
from products.views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'actors', ActorViewSet, basename='actor')

urlpatterns = [
    path('', include(router.urls)),
]
