from django.test import TestCase
from rest_framework.status import HTTP_400_BAD_REQUEST

from ..exceptions import InvalidExpiredToken


class InvalidExpiredTokenTest(TestCase):
    """Assert `InvalidExpiredToken` behaves as expected."""
    def test_raise(self):
        """Assert `InvalidExpiredToken` can be raised."""
        with self.assertRaises(InvalidExpiredToken) as e:
            raise InvalidExpiredToken
        self.assertEqual(e.exception.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(str(e.exception.detail), 'Invalid or expired token.')
