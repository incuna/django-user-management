from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from user_management.api.exceptions import InvalidExpiredToken


class VerifyAccountViewMixin(object):
    """
    Verify a new user's email address.

    Verify a newly created account by checking the `token` in the URL kwargs.
    """
    ok_message = _('Your account has been verified.')
    invalid_exception_class = InvalidExpiredToken
    permission_denied_class = PermissionDenied

    # Default token never expires.
    DEFAULT_VERIFY_ACCOUNT_EXPIRY = None

    def verify_token(self, request, *args, **kwargs):
        """
        Use `token` to allow one-time access to a view.

        Set the user as a class attribute or raise an `InvalidExpiredToken`.

        Token expiry can be set in `settings` with `VERIFY_ACCOUNT_EXPIRY` and is
        set in seconds.
        """
        User = get_user_model()

        try:
            max_age = settings.VERIFY_ACCOUNT_EXPIRY
        except AttributeError:
            max_age = self.DEFAULT_VERIFY_ACCOUNT_EXPIRY

        try:
            email_data = signing.loads(kwargs['token'], max_age=max_age)
        except signing.BadSignature:
            raise self.invalid_exception_class

        email = email_data['email']

        try:
            self.user = User.objects.get_by_natural_key(email)
        except User.DoesNotExist:
            raise self.invalid_exception_class

        if self.user.email_verified:
            raise self.permission_denied_class

    def activate_user(self):
        self.user.email_verified = True
        self.user.is_active = True
        self.user.save()
