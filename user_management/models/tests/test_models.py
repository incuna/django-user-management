from datetime import datetime
from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import models
from .factories import UserFactory


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
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.verified_email)

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


class TestUser(TestCase):
    def test_send_validation_email(self):
        site = Site.objects.get_current()
        subject = '{} account validate'.format(site.domain)
        template = 'user_management/account_validation_email.html'
        user = UserFactory.create()

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        with patch.object(default_token_generator, 'make_token') as make_token:
            with patch('user_management.models.mixins.send') as send:
                user.send_validation_email()

        send.assert_called_once_with(
            to=[user.email],
            subject=subject,
            template_name=template,
            extra_context={'token': make_token(), 'uid': uid},
        )

    def test_verified_email(self):
        user = UserFactory.create(verified_email=True)

        with patch('user_management.models.mixins.send') as send:
            with self.assertRaises(ValueError):
                user.send_validation_email()

        self.assertFalse(send.called)
