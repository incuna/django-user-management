import unittest

import django
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core import checks
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils import six
from django.utils.http import urlsafe_base64_encode
from mock import patch

from .. import mixins
from . import models
from .factories import UserFactory


skip_if_checks_unavailable = unittest.skipIf(
    django.VERSION < (1, 7),
    'Checks only available in django>=1.7',
)


class TestUser(TestCase):
    """Test the "User" model"""
    model = models.User

    def test_fields(self):
        """Do we have the fields we expect?"""
        fields = self.model._meta.get_all_field_names()
        expected = {
            # On model
            'id',
            'name',
            'date_joined',
            'email',
            'email_verification_required',
            'is_active',
            'is_staff',
            'is_superuser',
            'last_login',
            'password',
            'avatar',

            # Incoming
            'groups',  # Django permission groups
            'user_permissions',
            'logentry',  # Django admin logs
            'auth_token',  # Rest framework authtoken
        }

        try:
            # python 3 only:
            self.assertCountEqual(fields, expected)
        except AttributeError:
            # python 2 only:
            self.assertItemsEqual(fields, expected)

    def test_str(self):
        """Does "User.__str__()" work as expected?"""
        expected = 'Leopold Stotch'
        user = self.model(name=expected)
        self.assertEqual(six.text_type(user), expected)

    def test_name_methods(self):
        """Do "User.get_full_name()" & "get_short_name()" work as expected?"""
        expected = 'Professor Chaos'
        user = self.model(name=expected)
        self.assertEqual(user.get_full_name(), expected)
        self.assertEqual(user.get_short_name(), expected)


class TestUserManager(TestCase):
    manager = models.User.objects

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            self.manager.create_user(email='')
        self.assertFalse(self.manager.count())

    def test_create_duplicate_email(self):
        existing_user = UserFactory.create()
        with self.assertRaises(IntegrityError):
            self.manager.create_user(email=existing_user.email.upper())

    def test_create_user(self):
        time_before = timezone.now()
        data = {
            'email': 'valid@example.com',
            'name': 'Mysterion',
            'password': 'I can N3ver DIE!'
        }

        # Call creation method of manager
        with self.assertNumQueries(1):
            # Only one query:
            #     INSERT INTO "users_user" ("fields",)
            #         VALUES ('blah') RETURNING "users_user"."id"
            result = self.manager.create_user(**data)

        # Check that user returned is the right one
        user = self.manager.get()
        self.assertEqual(user, result)

        # Check that the password is valid
        self.assertTrue(user.check_password(data['password']))

        # Check name/email is correct
        self.assertEqual(user.name, data['name'])
        self.assertEqual(user.email, data['email'])

        # Check defaults
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.email_verification_required)

        # Check that the time is correct (or at least, in range)
        time_after = timezone.now()
        self.assertTrue(time_before < user.date_joined < time_after)

    def test_create_user_uppercase_email(self):
        email = 'VALID@EXAMPLE.COM'

        user = self.manager.create_user(email)
        self.assertEqual(email.lower(), user.email)

    def test_create_superuser(self):
        email = 'valid@example.com'
        password = 'password'

        # Call creation method of manager:
        with self.assertNumQueries(1):
            # Only one query:
            #     INSERT INTO "users_user" ("fields",)
            #         VALUES ('blah') RETURNING "users_user"."id"
            result = self.manager.create_superuser(email, password)

        # Check that user returned is the right one
        user = self.manager.get()
        self.assertEqual(user, result)

        # Check that the password is valid
        self.assertTrue(user.check_password(password))

        # Check defaults
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class TestVerifyEmailMixin(TestCase):
    model = models.VerifyEmailUser

    def test_save(self):
        user = self.model()
        user.save()
        self.assertFalse(user.is_active)
        self.assertTrue(user.email_verification_required)

    def test__email_context(self):
        site = Site.objects.get_current()
        user = self.model()
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        with patch.object(default_token_generator, 'make_token') as make_token:
            context = user._get_email_context(site)

        expected_context = {'uid': uid, 'token': make_token(), 'site': site}
        self.assertEqual(context, expected_context)

    def test__get_email_kwargs(self):
        context = {}
        domain = 'http://example.com'
        subject = '{domain} registration'
        text_template = 'user_management/account_validation_email.txt'

        user = self.model(email='dummy@example.com')
        user.EMAIL_SUBJECT_TEMPLATE = subject

        kwargs = user._get_email_kwargs(context, domain)

        expected_kwargs = {
            'to': [user.email],
            'template_name': text_template,
            'subject': subject.format(domain=domain),
            'context': context,
        }
        self.assertEqual(kwargs, expected_kwargs)

    def test_send_validation_email(self):
        context = {}
        kwargs = {'context': context}
        site = Site.objects.get_current()
        user = self.model()

        with patch.object(user, '_get_email_context') as get_context:
            get_context.return_value = context
            with patch.object(user, '_get_email_kwargs') as get_kwargs:
                get_kwargs.return_value = kwargs
                with patch('user_management.models.mixins.send') as send:
                    user.send_validation_email()

        get_kwargs.assert_called_once_with(context, site.domain)
        send.assert_called_once_with(**kwargs)

    def test_verified_email(self):
        user = self.model(email_verification_required=False)

        with patch('user_management.models.mixins.send') as send:
            with self.assertRaises(ValueError):
                user.send_validation_email()

        self.assertFalse(send.called)

    @skip_if_checks_unavailable
    def test_manager_check_valid(self):
        errors = self.model.check()
        self.assertEqual(errors, [])

    @skip_if_checks_unavailable
    def test_manager_check_invalid(self):
        class InvalidUser(self.model):
            objects = mixins.UserManager()

        expected = [
            checks.Warning(
                "Manager should be an instance of 'VerifyEmailManager'",
                hint="Subclass a custom manager from 'VerifyEmailManager'",
                obj=InvalidUser,
                id='user_management.W001',
            ),
        ]
        errors = InvalidUser.check()
        self.assertEqual(errors, expected)
