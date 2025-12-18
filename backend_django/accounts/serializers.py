# accounts/serializers.py
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User

class UserSerializer(serializers.ModelSerializer):
    # password нужно write_only, но мы хотим вернуть его при создании
    password = serializers.CharField(write_only=True, required=False)
    generated_password = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'login', 'password', 'generated_password', 'role', 'actors', 'is_active']

    def create(self, validated_data):
        # Если пароль не передан, создаём автоматически
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        # Добавляем поле generated_password для возврата в ответе
        user.generated_password = password or user.password  # если сгенерирован, вернём plain text
        return user

    def to_representation(self, instance):
        # Стандартное представление
        ret = super().to_representation(instance)
        if hasattr(instance, 'generated_password'):
            ret['password'] = instance.generated_password
        return ret

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Можно добавить кастомные поля
        token['username'] = user.username
        return token