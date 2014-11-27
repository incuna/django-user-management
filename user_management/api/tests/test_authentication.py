import mock
from django.http import QueryDict
from django.test import TestCase

from ..authentication import FormTokenAuthentication
from user_management.models.tests.factories import AuthTokenFactory


class TestFormTokenAuthentication(TestCase):
    def test_no_token(self):
        request = mock.Mock(DATA=QueryDict(''))
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_invalid_token(self):
        data = QueryDict('', mutable=True)
        data.update({'token': 'WOOT'})
        request = mock.Mock(DATA=data)
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_valid_token(self):
        token = AuthTokenFactory.create()
        data = QueryDict('', mutable=True)
        data.update({'token': token.key})
        request = mock.Mock(DATA=data)
        response = FormTokenAuthentication().authenticate(request)
        expected = (token.user, token)
        self.assertEqual(response, expected)
