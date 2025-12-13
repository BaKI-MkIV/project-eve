# accounts/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import MyTokenObtainPairSerializer, UserSerializer

# Логин — использует наш кастомный сериализатор
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Профиль текущего пользователя
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# Logout — blacklist refresh token
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Успешно вышел."}, status=205)
        except Exception as e:
            return Response({"error": "Неверный токен."}, status=400)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login = request.data.get('login')
        password = request.data.get('password')
        role = request.data.get('role', 'player')  # По умолчанию player

        if not login or not password:
            return Response({"error": "Логин и пароль обязательны"}, status=400)

        if User.objects.filter(login=login).exists():
            return Response({"error": "Логин уже занят"}, status=400)

        user = User.objects.create_user(
            login=login,
            password=password,
            role=role
        )

        # Опционально: сразу выдать токены
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=201)