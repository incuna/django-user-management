from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsNotAuthenticated(BasePermission):
    """Permit only users that are NOT logged in!"""
    def has_permission(self, request, view):
        return request.user.is_anonymous


class IsAdminOrReadOnly(BasePermission):
    """
    Ensures user is staff when creating or updating an user otherwise return a
    HTTP forbidden (403)
    """
    def has_permission(self, request, view):
        # safe methods are get, head, options
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff
