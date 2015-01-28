from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidExpiredToken(APIException):
    """Exception to confirm an account."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid or expired token.')
