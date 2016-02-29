from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from user_management.utils.views import VerifyAccountViewMixin
from .exceptions import InvalidExpiredToken


class VerifyUserEmailView(VerifyAccountViewMixin, generic.RedirectView):
    """
    A view which verifies a user's email address.

    Accessed via a link in an email sent to the user, which contains both a
    uid generated from the user's pk, and a token also generated from the user
    object, for verification.  If everything lines up, it makes the user
    active.

    As a RedirectView, this will return a HTTP 302 on success.  This defaults to
    `/` but can be overridden by changing the `url` attribute in a subclass.
    """
    permanent = False
    url = '/'
    success_message = _('Your email address was confirmed.')
    invalid_exception_class = InvalidExpiredToken
    permission_denied_class = PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        self.verify_token(request, *args, **kwargs)
        return super(VerifyUserEmailView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.activate_user()
        messages.success(request, self.success_message)

        # Redirect using the generic view's get method.
        return super(VerifyUserEmailView, self).get(request, *args, **kwargs)
