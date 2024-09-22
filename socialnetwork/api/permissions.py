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
    
class IsNotBlocked(BasePermission):
    """
    Custom permission to prevent blocked users from accessing certain endpoints.
    """
    def has_permission(self, request, view):
        # Check if the requesting user is blocked by the profile owner
        if request.user.is_authenticated:
            blocked_users = BlockedUser.objects.filter(blocked_user=request.user).values_list('blocked_by_id', flat=True)
            # Assuming 'profile_owner' is passed in request or obtained from view logic
            profile_owner_id = view.kwargs.get('profile_owner_id')
            if profile_owner_id in blocked_users:
                return False
        return True
