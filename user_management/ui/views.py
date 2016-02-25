from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views import generic


class VerifyUserEmailView(generic.RedirectView):
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

    def get(self, request, *args, **kwargs):
        # Retrieve and decode the UID.
        uidb64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(force_text(uidb64))
        User = get_user_model()
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise Http404

        # Retrieve and check the token.
        token = kwargs['token']
        if not default_token_generator.check_token(user, token):
            raise Http404

        # Return a 403 if the user doesn't need verifying.
        if user.email_verified:
            raise PermissionDenied

        # All's well, so activate the user.
        user.email_verified = True
        user.is_active = True
        user.save()
        messages.success(request, self.success_message)

        # Redirect using the generic view's get method.
        return super(VerifyUserEmailView, self).get(request, *args, **kwargs)
