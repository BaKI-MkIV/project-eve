from rest_framework import permissions


class IsMasterOrReadOnly(permissions.BasePermission):
    """
    Изменять может только мастер (is_staff),
    читать могут все.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsAutomat(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.role == 'automat'
        )


class IsMaster(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_staff and
            request.user.role == 'master'
        )