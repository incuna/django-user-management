import datetime

import mock
from django.test.utils import override_settings

from ..management.commands import remove_expired_tokens
from user_management.api.models import AuthToken
from user_management.models.tests import utils
from user_management.models.tests.factories import AuthTokenFactory


class TestRemoveExpiredTokensManagementCommand(utils.APIRequestTestCase):
    def setUp(self):
        self.command = remove_expired_tokens.Command()
        self.command.stdout = mock.MagicMock()

    def test_no_tokens_removed(self):
        """Tests that non-expired tokens are not removed."""
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        token = AuthTokenFactory.create(expires=tomorrow)

        self.command.handle()

        expected = AuthToken.objects.all()
        self.assertCountEqual(expected, [token])

    @override_settings(AUTH_TOKEN_MAX_EXPIRY=7)
    def test_expired_tokens(self):
        """Ensure expired token is removed from db while valid one remains."""
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        valid_token = AuthTokenFactory.create(expires=tomorrow)

        # this token is expired
        long_ago = now - datetime.timedelta(days=33)
        AuthTokenFactory.create(expires=long_ago)

        self.command.handle()
        expected = AuthToken.objects.all()

        self.assertCountEqual(expected, [valid_token])
