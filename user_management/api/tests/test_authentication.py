import datetime

import mock
from django.http import QueryDict
from django.test import TestCase
from django.utils import timezone
from rest_framework import exceptions

from user_management.models.tests.factories import AuthTokenFactory, UserFactory
from ..authentication import FormTokenAuthentication, TokenAuthentication


class TestFormTokenAuthentication(TestCase):
    def test_no_token(self):
        request = mock.Mock(data=QueryDict(''))
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_invalid_token(self):
        data = QueryDict('', mutable=True)
        data.update({'token': 'WOOT'})
        request = mock.Mock(data=data)
        response = FormTokenAuthentication().authenticate(request)
        self.assertIsNone(response)

    def test_valid_token(self):
        token = AuthTokenFactory.create()
        data = QueryDict('', mutable=True)
        data.update({'token': token.key})
        request = mock.Mock(data=data)
        response = FormTokenAuthentication().authenticate(request)
        expected = (token.user, token)
        self.assertEqual(response, expected)


class TestTokenAuthentication(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.days = 1
        self.key = 'k$y'
        self.user = UserFactory.create()
        self.auth = TokenAuthentication()

    def _create_token(self, when):
        token = AuthTokenFactory.create(
            key=self.key,
            user=self.user,
            expires=when,
        )

        return token

    def test_token_expiry_if_valid(self):
        # Token is valid till tomorrow
        tomorrow = self.now + datetime.timedelta(days=self.days)
        token_old = self._create_token(when=tomorrow)

        user, token = self.auth.authenticate_credentials(self.key)

        self.assertEqual(token, token_old)
        self.assertEqual(user, self.user)

    def test_token_expiry_if_has_expired(self):
        # Token has expired yesterday
        yesterday = self.now - datetime.timedelta(days=self.days)
        self._create_token(when=yesterday)

        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate_credentials(self.key)

    def test_token_inactivity(self):
        # Create token valid till tomorrow
        tomorrow = self.now + datetime.timedelta(days=self.days)
        token_example = self._create_token(when=tomorrow)

        user, token = self.auth.authenticate_credentials(self.key)

        # Ensure tokens are correct
        self.assertEqual(token, token_example)

        # Auth again with very low inactivity time
        # Token's expiry gets updated in auth process
        with self.settings(AUTH_TOKEN_MAX_INACTIVITY=0):
            self.auth.authenticate_credentials(self.key)

        # User's token has expired now
        with self.assertRaises(exceptions.AuthenticationFailed):
            self.auth.authenticate_credentials(self.key)
