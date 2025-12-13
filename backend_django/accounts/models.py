# accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Login должен быть указан')

        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'master')  # Суперюзер = мастер

        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="Уникальный логин (не email)"
    )

    role = models.CharField(
        max_length=10,
        choices=[('player', 'Player'), ('master', 'Master')],
        default='player'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Для доступа в админку

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'  # Под каким полем логинимся
    REQUIRED_FIELDS = []  # Дополнительные обязательные поля при createsuperuser

    def __str__(self):
        return self.login

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']