from rest_framework.permissions import BasePermission

class IsReadOnly(BasePermission):
    """
    Allows access only to users with 'Read' or higher roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['Read', 'Write', 'Admin']

class IsWrite(BasePermission):
    """
    Allows access only to users with 'Write' or 'Admin' roles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['Write', 'Admin']

class IsAdmin(BasePermission):
    """
    Allows access only to users with 'Admin' role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Admin'
