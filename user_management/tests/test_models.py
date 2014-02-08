from datetime import datetime
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from . import models


class TestUserManager(TestCase):
    manager = models.User.objects

    def test_create_user(self):
        email = 'valid@example.com'
        signup_datetime = timezone.make_aware(
            datetime(2013, 11, 28, 12, 29), timezone.utc,
        )

        with patch.object(timezone, 'now') as mocked_now:
            mocked_now.return_value = signup_datetime
            user = self.manager.create_user(email)

        self.assertEqual(email, user.email)
        self.assertEqual(signup_datetime, user.date_joined)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_uppercase_email(self):
        email = 'VALID@EXAMPLE.COM'

        user = self.manager.create_user(email)
        self.assertEqual(email.lower(), user.email)

    def test_create_superuser(self):
        email = 'valid@example.com'
        password = 'password'

        user = self.manager.create_superuser(email, password)

        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
