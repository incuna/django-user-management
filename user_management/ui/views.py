from django.conf import settings
from django.contrib import auth, messages
from django.shortcuts import resolve_url
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from user_management.utils.views import VerifyAccountViewMixin
from .exceptions import AlreadyVerifiedException, InvalidExpiredToken


class VerifyUserEmailView(VerifyAccountViewMixin, generic.RedirectView):
    """
    A view which verifies a user's email address.

    Accessed via a link in an email sent to the user, which contains both a
    uid generated from the user's pk, and a token also generated from the user
    object, for verification.  If everything lines up, it makes the user
    active.

    As a RedirectView, this will return a HTTP 302 to LOGIN_URL on success.
    """
    permanent = False
    already_verified = False
    success_message = _('Your email address was confirmed.')
    already_verified_message = _('Your email is already confirmed.')
    invalid_exception_class = InvalidExpiredToken
    permission_denied_class = AlreadyVerifiedException

    def get_redirect_url(self, *args, **kwargs):
        query_string = getattr(settings, 'VERIFIED_QUERYSTRING', '')
        url_extra = ''

        if query_string and not self.already_verified:
            url_extra = '?' + query_string

        return resolve_url(settings.LOGIN_URL) + url_extra

    def dispatch(self, request, *args, **kwargs):
        try:
            self.verify_token(request, *args, **kwargs)
        except self.permission_denied_class:
            self.already_verified = True
            self.success_message = self.already_verified_message
        return super(VerifyUserEmailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        auto_login = getattr(settings, 'LOGIN_ON_EMAIL_VERIFICATION', False)

        if not self.already_verified:
            self.activate_user()
            if auto_login is True:
                self.user.backend = settings.AUTHENTICATION_BACKENDS[0]
                auth.login(request=request, user=self.user)
        messages.success(request, self.success_message)
        return super(VerifyUserEmailView, self).get(request, *args, **kwargs)
