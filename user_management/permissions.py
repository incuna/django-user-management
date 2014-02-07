from rest_framework.permissions import BasePermission


class IsNotAuthenticated(BasePermission):
    """Permit only users that are NOT logged in!"""
    def has_permission(self, request, view):
        return request.user.is_anonymous()
