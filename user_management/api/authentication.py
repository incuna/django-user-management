from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import authentication, exceptions
from rest_framework.authentication import TokenAuthentication as DRFTokenAuthentication

from .models import AuthToken


class FormTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        Authenticate a user from a token form field

        Errors thrown here will be swallowed by django-rest-framework, and it
        expects us to return None if authentication fails.
        """
        try:
            key = request.DATA['token']
        except KeyError:
            return

        try:
            token = AuthToken.objects.get(key=key)
        except AuthToken.DoesNotExist:
            return

        return (token.user, token)


class TokenAuthentication(DRFTokenAuthentication):
    model = AuthToken

    def authenticate_credentials(self, key):
        """Custom authentication to check if auth token has expired."""
        user, token = super(TokenAuthentication, self).authenticate_credentials(key)

        if token.expires < timezone.now():
            msg = _('Token has expired.')
            raise exceptions.AuthenticationFailed(msg)

        # Update the token's expiration date
        token.update_expiry()

        return (user, token)
