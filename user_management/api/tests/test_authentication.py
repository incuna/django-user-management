import mock
from django.test import TestCase

from ..authentication import FormTokenAuthentication
from user_management.models.tests.factories import TokenFactory


class TestFormTokenAuthentication(TestCase):
    def test_no_token(self):
        request = mock.Mock(DATA={})
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_invalid_token(self):
        request = mock.Mock(DATA={'token': ['WOOT']})
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_valid_token(self):
        token = TokenFactory.create()
        request = mock.Mock(DATA={'token': [token.key]})
        response = FormTokenAuthentication().authenticate(request)
        expected = (token.user, token)
        self.assertEqual(response, expected)
