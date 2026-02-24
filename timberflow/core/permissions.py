from rest_framework.permissions import BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Allow read access to all authenticated users, write access to admins only."""

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(BasePermission):
    """Allow access only to the object owner or admins."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        created_by = getattr(obj, 'created_by', None)
        return created_by == request.user
