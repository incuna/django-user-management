from django.http import Http404
from django.utils.translation import ugettext_lazy as _


class InvalidExpiredToken(Http404):
    """Exception to confirm an account."""
    message = _('Invalid or expired token.')
