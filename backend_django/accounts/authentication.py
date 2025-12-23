from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()

class AutomatTokenAuthentication(authentication.BaseAuthentication):
    """
    Простая авторизация по токену для системных скриптов/модулей (Automat).
    Например, передаём токен через заголовок `Authorization: Automat <token>`.
    """
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            auth_type, token = auth_header.split()
        except ValueError:
            raise exceptions.AuthenticationFailed('Неправильный формат заголовка Authorization')

        if auth_type.lower() != 'automat':
            return None

        # Здесь проверяем token, например, сопоставляем с полем в базе
        try:
            user = User.objects.get(role='automat', login=token)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Неверный токен')

        return (user, None)
