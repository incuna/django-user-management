from django.test import TestCase
from rest_framework.status import HTTP_400_BAD_REQUEST

from ..exceptions import InvalidExpiredToken


class InvalidExpiredTokenTest(TestCase):
    """Assert `InvalidExpiredToken` behaves as expected."""
    def test_raise(self):
        """Assert `InvalidExpiredToken` can be raised."""
        with self.assertRaises(InvalidExpiredToken) as error:
            raise InvalidExpiredToken
        self.assertEqual(error.exception.status_code, HTTP_400_BAD_REQUEST)
        message = error.exception.detail.format()
        self.assertEqual(message, 'Invalid or expired token.')
