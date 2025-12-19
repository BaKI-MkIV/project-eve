from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    MyTokenObtainPairView,
    MyTokenRefreshView,
    UserMeView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # auth
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user-me'),

    # master
    path('', include(router.urls)),
]
