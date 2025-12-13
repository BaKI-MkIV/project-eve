from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=128)

    role = models.CharField(
        max_length=10,
        choices=[('player', 'Player'), ('master', 'Master')],
        default='player'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'login'