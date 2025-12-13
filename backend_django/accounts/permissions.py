# accounts/permissions.py
from rest_framework import permissions

class IsMasterUser(permissions.BasePermission):
    """
    Разрешить доступ только пользователям с role='master'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'master')
