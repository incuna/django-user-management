from django.test import TestCase

from ..exceptions import InvalidExpiredToken


class TestInvalidExpiredToken(TestCase):
    """Assert `InvalidExpiredToken` behaves as expected."""
    def test_raise(self):
        """Assert `InvalidExpiredToken` can be raised."""
        with self.assertRaises(InvalidExpiredToken) as error:
            raise InvalidExpiredToken

        self.assertEqual(error.exception.message, 'Invalid or expired token.')
