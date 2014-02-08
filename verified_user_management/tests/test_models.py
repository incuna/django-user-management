from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_management.tests.factories import UserFactory
from .models import User


class TestUser(TestCase):
    def test_create_user(self):
        email = 'valid@example.com'
        with patch.object(User, 'send_validation_email') as send:
            user = User.objects.create_user(email)
        self.assertEqual(email, user.email)
        self.assertFalse(user.is_active)
        self.assertFalse(user.verified_email)
        send.assert_called_once_with()

    def test_send_validation_email(self):
        site = Site.objects.get_current()
        subject = '{} account validate'.format(site.domain)
        template = 'user_management/account_validation_email.html'
        user = UserFactory.create()

        uid = urlsafe_base64_encode(force_bytes(user.pk))

        with patch.object(default_token_generator, 'make_token') as make_token:
            with patch('verified_user_management.models.send') as send:
                user.send_validation_email()

        send.assert_called_once_with(
            to=[user.email],
            subject=subject,
            template_name=template,
            extra_context={'token': make_token(), 'uid': uid},
        )

    def test_verified_email(self):
        user = UserFactory.create(verified_email=True)

        with patch('verified_user_management.models.send') as send:
            with self.assertRaises(ValueError):
                user.send_validation_email()

        self.assertFalse(send.called)
