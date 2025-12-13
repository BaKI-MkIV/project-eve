# accounts/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import User
from actors.models import Actor


# Кастомный сериализатор для JWT — логин по полю login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'  # Это ключевой момент!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Заменяем поле username на login в форме
        self.fields['login'] = serializers.CharField()
        self.fields.pop('username', None)

    def validate(self, attrs):
        login = attrs.pop('login', None)
        if login:
            attrs['login'] = login
        return super().validate(attrs)


# Опционально: сериализатор для профиля /me
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # Это твой accounts.User
        fields = ['id', 'login', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']

class CreateUserSerializer(serializers.Serializer):
    actor_id = serializers.IntegerField(required=False, allow_null=True)  # Опционально: ID существующего актора
    role = serializers.ChoiceField(choices=['player', 'master'], default='player')  # По умолчанию player

    def validate_actor_id(self, value):
        if value:
            try:
                actor = Actor.objects.get(id=value)
                if actor.user:
                    raise serializers.ValidationError("Этот актор уже привязан к другому пользователю.")
                if actor.type != 'player':
                    raise serializers.ValidationError("Актор должен быть типа 'player'.")
            except Actor.DoesNotExist:
                raise serializers.ValidationError("Актор с таким ID не существует.")
        return value