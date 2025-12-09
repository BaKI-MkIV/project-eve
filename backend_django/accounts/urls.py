from django.urls import path
from .views import MyTokenObtainPairView, RegisterView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
]