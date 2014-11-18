from rest_framework import authentication
from rest_framework.authtoken.models import Token


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
            token = Token.objects.get(key=key)
        except Token.DoesNotExist:
            return

        return (token.user, token)
