# accounts/serializers.py

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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