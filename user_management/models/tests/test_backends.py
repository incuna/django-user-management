from django.test import TestCase

from .factories import UserFactory
from ..backends import CaseInsensitiveEmailBackend


class CaseInsensitveEmailBackendTest(TestCase):
    request = 'any'

    def test_authenticate(self):
        """
        Check case-insensitive username authentication
        """

        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        user = UserFactory.create(email=email, password=password, is_active=True)

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(
            self.request,
            username='Test-email@example.com',
            password=password,
        )

        self.assertEqual(user, authenticated_user)

    def test_authenticate_no_username(self):
        """
        Passing USERNAME_FIELD to authenticate is valid
        """

        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        user = UserFactory.create(email=email, password=password, is_active=True)

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(
            self.request,
            email='Test-email@example.com',
            password=password,
        )

        self.assertEqual(user, authenticated_user)

    def test_authenticate_no_user(self):
        """
        If no username is provided, just return None
        """

        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(
            self.request,
            email=email,
            password=password,
        )

        self.assertIs(authenticated_user, None)
