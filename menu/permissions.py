from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Any authenticated user can view menu items. Only staff/admin accounts
    (is_staff=True) can create, update, or delete them.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
