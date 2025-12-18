# backend_django/accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string


def generate_login():
    return 'player' + get_random_string(5)

def generate_password():
    return get_random_string(10)


class UserManager(BaseUserManager):
    def create_user(self, login=None, password=None, role='player', **extra_fields):
        if not login:
            login = generate_login()
        if not password:
            password = generate_password()

        user = self.model(login=login, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, role='master', **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('player', 'Player'),
        ('master', 'Master'),
    )

    id = models.BigAutoField(primary_key=True)
    login = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Для доступа в админку

    # Основная связь с актором (для игрока)
    actor = models.ForeignKey(
        'actors.Actor',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users'
    )

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.login} ({self.get_role_display()})"

    class Meta:
        constraints = [
            # Для мастера actors всегда null
            models.CheckConstraint(
                condition=Q(role='player') | Q(actor__isnull=True),
                name='master_actor_must_be_null'
            )
        ]
