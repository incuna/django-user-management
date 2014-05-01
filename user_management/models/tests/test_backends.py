from django.test import TestCase

from ..backends import CaseInsensitiveEmailBackend
from .factories import UserFactory


class CaseInsensitveEmailBackendTest(TestCase):
    def test_authenticate(self):
        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        user = UserFactory.create(email=email, password=password, is_active=True)

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(
            username='Test-email@example.com', password=password)

        self.assertEqual(user, authenticated_user)

    def test_authenticate_no_username(self):
        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        user = UserFactory.create(email=email, password=password, is_active=True)

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(
            email='Test-email@example.com', password=password)

        self.assertEqual(user, authenticated_user)

    def test_authenticate_no_user(self):
        email = 'test-Email@example.com'
        password = 'arandomsuperstrongpassword'

        backend = CaseInsensitiveEmailBackend()
        authenticated_user = backend.authenticate(email=email, password=password)

        self.assertIs(authenticated_user, None)
