# accounts/views.py
import uuid

from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from actors.models import Actor
from economy.models import ActorBalance
from economy.serializers import WalletSerializer
from inventory.models import InventoryItem
from inventory.serializers import InventorySerializer
from .permissions import IsMasterUser
from .serializers import MyTokenObtainPairSerializer, UserSerializer, CreateUserSerializer

from actors.models import Actor
from actors.serializers import PublicActorSerializer, UpdateMeActorSerializer


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


# class RegisterView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request):
#         login = request.data.get('login')
#         password = request.data.get('password')
#         role = request.data.get('role', 'player')  # По умолчанию player
#
#         if not login or not password:
#             return Response({"error": "Логин и пароль обязательны"}, status=400)
#
#         if User.objects.filter(login=login).exists():
#             return Response({"error": "Логин уже занят"}, status=400)
#
#         user = User.objects.create_user(
#             login=login,
#             password=password,
#             role=role
#         )
#
#         # Опционально: сразу выдать токены
#         refresh = RefreshToken.for_user(user)
#         return Response({
#             "user": UserSerializer(user).data,
#             "refresh": str(refresh),
#             "access": str(refresh.access_token),
#         }, status=201)

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    """
    Только для мастера:
    - GET    /users/       — список всех пользователей
    - POST   /users/       — создать пользователя с генерацией логина/пароля
    """
    permission_classes = [IsMasterUser]

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Генерация случайного логина и пароля
        login = f"player_{uuid.uuid4().hex[:10]}"  # Пример: player_a1b2c3d4e5
        raw_password = uuid.uuid4().hex[:12]       # 12 символов — безопасно и удобно

        # Создаём пользователя
        user = User.objects.create_user(
            login=login,
            password=raw_password,
            role=serializer.validated_data['role']
        )

        # Привязываем или создаём актора
        actor_id = serializer.validated_data.get('actor_id')
        if actor_id:
            actor = Actor.objects.get(id=actor_id)
        else:
            # Создаём новый generic актор
            actor = Actor.objects.create(
                name=login,  # Можно сделать f"Игрок {uuid.uuid4().hex[:6]}", если хочешь анонимнее
                type='player',
                user=user,
                is_hidden=False,
                is_system=False
            )

        # Привязка (на всякий случай, если был указан actor_id)
        actor.user = user
        actor.save()

        return Response({
            "user_id": user.id,
            "login": login,
            "raw_password": raw_password,  # Мастер передаст игроку вручную
            "actor_id": actor.id,
            "actor_name": actor.name,
            "message": "Пользователь создан. Передайте логин и пароль игроку."
        }, status=status.HTTP_201_CREATED)


from rest_framework.decorators import api_view, permission_classes

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    errors = {}

    if 'login' in data:
        new_login = data['login'].strip()
        if not new_login:
            errors['login'] = "Логин не может быть пустым"
        elif User.objects.filter(login=new_login).exclude(pk=user.pk).exists():
            errors['login'] = "Этот логин уже занят"
        else:
            user.login = new_login

    if 'password' in data:
        new_password = data['password']
        if len(new_password) < 8:
            errors['password'] = "Пароль должен быть не менее 8 символов"
        else:
            user.set_password(new_password)

    if errors:
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    user.save()
    return Response({
        "message": "Профиль обновлён",
        "login": user.login
    })

class MeActorViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        """
        GET /auth/me/actor/
        Возвращает данные своего актора
        """
        user = request.user
        try:
            actor = user.actor  # Через related_name='actor'
        except Actor.DoesNotExist:
            return Response({"error": "У вас нет привязанного актора"}, status=404)

        serializer = PublicActorSerializer(actor)
        return Response(serializer.data)

    def partial_update(self, request):
        """
        PATCH /auth/me/actor/
        Обновляет имя и/или описание
        """
        user = request.user
        try:
            actor = user.actor
        except Actor.DoesNotExist:
            return Response({"error": "У вас нет привязанного актора"}, status=404)

        serializer = UpdateMeActorSerializer(actor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class MeWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            actor = user.actor
        except Actor.DoesNotExist:
            return Response({"error": "Актор не найден"}, status=404)

        balances = ActorBalance.objects.filter(actor=actor)
        serializer = WalletSerializer(balances, many=True)
        return Response(serializer.data)


class MeInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            actor = user.actor
        except Actor.DoesNotExist:
            return Response({"error": "Актор не найден"}, status=404)

        items = InventoryItem.objects.filter(actor=actor).select_related('product')
        serializer = InventorySerializer(items, many=True)
        return Response(serializer.data)