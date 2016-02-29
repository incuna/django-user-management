import mock
from django.contrib.auth import get_user_model
from django.test import override_settings

from user_management.models.tests.factories import VerifyEmailUserFactory
from user_management.models.tests.utils import APIRequestTestCase
from .. import views

User = get_user_model()


@override_settings(AUTH_USER_MODEL='tests.VerifyEmailUser')
class TestVerifyAccountView(APIRequestTestCase):
    view_class = views.VerifyAccountViewMixin

    @classmethod
    def setUpTestData(cls):
        cls.request = mock.MagicMock
        cls.view_instance = cls.view_class()
        cls.user = VerifyEmailUserFactory.create(email_verified=False)
        cls.token = cls.user.generate_validation_token()

    def test_verify_token_allowed(self):
        """Assert a user can verify its own email."""
        self.view_instance.verify_token(self.request, token=self.token)
        self.assertEqual(self.view_instance.user, self.user)

    def test_verify_token_invalid_user(self):
        """Assert a nonexistent user throws an exception."""
        user = VerifyEmailUserFactory.build()
        token = user.generate_validation_token()
        with self.assertRaises(self.view_instance.invalid_exception_class):
            self.view_instance.verify_token(self.request, token=token)

    def test_verify_token_invalid_token(self):
        """Assert forged token return a bad request."""
        token = 'nimporte-nawak'
        with self.assertRaises(self.view_instance.invalid_exception_class):
            self.view_instance.verify_token(self.request, token=token)

    def test_default_expiry_token(self):
        """Assert `DEFAULT_VERIFY_ACCOUNT_EXPIRY` doesn't expire by default."""
        with mock.patch('django.core.signing.loads') as signing_loads:
            signing_loads.return_value = {'email': self.user.email}
            self.view_instance.verify_token(self.request, token=self.token)

        signing_loads.assert_called_once_with(self.token, max_age=None)

    @override_settings(VERIFY_ACCOUNT_EXPIRY=0)
    def test_verify_token_expired_token(self):
        """Assert token expires when VERIFY_ACCOUNT_EXPIRY is set."""
        with self.assertRaises(self.view_instance.invalid_exception_class):
            self.view_instance.verify_token(self.request, token=self.token)

    def test_verify_token_verified_email(self):
        """Assert verified user cannot verify email."""
        user = VerifyEmailUserFactory.create(email_verified=True)
        token = user.generate_validation_token()
        with self.assertRaises(self.view_instance.permission_denied_class):
            self.view_instance.verify_token(self.request, token=token)

    def test_activate_user(self):
        user = VerifyEmailUserFactory.create(email_verified=False, is_active=False)
        self.view_instance.user = user

        self.view_instance.activate_user()
        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)
