# accounts/views.py
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import UserSerializer, MyTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Простейшие разрешения: игрок может редактировать только себя, админ — всех
    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    # Ограничение, чтобы игрок видел/менял только себя
    def get_queryset(self):
        user = self.request.user
        if user.role == 'player':
            return User.objects.filter(id=user.id)
        return super().get_queryset()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class MyTokenRefreshView(TokenRefreshView):
    pass