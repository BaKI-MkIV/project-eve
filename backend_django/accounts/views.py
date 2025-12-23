# accounts/views.py
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User, AutomatToken
from .serializers import UserSelfSerializer, UserMasterSerializer, MyTokenObtainPairSerializer


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSelfSerializer

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


class AutomatTokenAuthentication(BaseAuthentication):
    keyword = 'Automat'

    def authenticate(self, request):
        header = request.headers.get('Authorization')
        if not header:
            return None

        try:
            keyword, token = header.split()
        except ValueError:
            return None

        if keyword != self.keyword:
            return None

        try:
            token_obj = AutomatToken.objects.select_related('user').get(
                token=token,
                is_active=True
            )
        except AutomatToken.DoesNotExist:
            raise AuthenticationFailed('Invalid automat token')

        return (token_obj.user, None)