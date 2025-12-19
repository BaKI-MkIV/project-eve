# accounts/views.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import UserSelfSerializer, UserMasterSerializer, MyTokenObtainPairSerializer


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['auth'], description='Информация о текущем пользователе')
    def get(self, request):
        serializer = UserSelfSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(tags=['auth'], description='Обновление данных текущего пользователя')
    def patch(self, request):
        serializer = UserSelfSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserMasterSerializer
    permission_classes = [permissions.IsAdminUser]


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    @extend_schema(tags=['auth'], description='Получение JWT токена')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MyTokenRefreshView(TokenRefreshView):
    @extend_schema(tags=['auth'], description='Обновление access токена')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)