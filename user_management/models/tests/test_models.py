# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.core import checks
from django.db.models import TextField
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from mock import Mock, patch

from user_management.models.tests import utils
from user_management.utils.notifications import validation_email_context
from . import models
from .factories import UserFactory
from .. import mixins


PASSWORD_CONTEXT = 'user_management.utils.notifications.password_reset_email_context'
VALIDATION_CONTEXT = 'user_management.utils.notifications.validation_email_context'
SEND_METHOD = 'user_management.utils.notifications.incuna_mail.send'


class TestUser(utils.APIRequestTestCase):
    """Test the "User" model"""
    model = models.User

    def test_fields(self):
        """Do we have the fields we expect?"""
        fields = {field.name for field in self.model._meta.get_fields()}
        expected = {
            # On model
            'id',
            'name',
            'date_joined',
            'email',
            'email_verified',
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
            'authtoken',
            'auth_token',  # Rest framework authtoken
        }

        self.assertCountEqual(fields, expected)

    def test_str(self):
        """Does "User.__str__()" work as expected?"""
        expected = 'Leopold Stotch'
        user = self.model(name=expected)
        self.assertEqual(str(user), expected)

    def test_name_methods(self):
        """Do "User.get_full_name()" & "get_short_name()" work as expected?"""
        expected = 'Professor Chaos'
        user = self.model(name=expected)
        self.assertEqual(user.get_full_name(), expected)
        self.assertEqual(user.get_short_name(), expected)

    def test_case_insensitive_uniqueness(self):
        self.model(email='CAPS@example.com').save()
        with self.assertRaises(IntegrityError):
            self.model(email='caps@example.com').save()


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
        self.assertFalse(user.email_verified)

        # Check that the time is correct (or at least, in range)
        time_after = timezone.now()
        self.assertTrue(time_before < user.date_joined < time_after)

    def test_create_user_uppercase_email(self):
        email = 'VALID@EXAMPLE.COM'

        user = self.manager.create_user(email)
        self.assertEqual(email.lower(), user.email)

    def test_set_last_login(self):
        email = 'valid@example.com'

        before = timezone.now()
        user = self.manager.create_user(email)
        after = timezone.now()

        self.assertTrue(before < user.last_login < after)

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

    def test_get_by_natural_key(self):
        """Assert email is case-insensitive."""
        email = 'WHATDID@YOU.SAY'
        existing_user = UserFactory.create(email=email)

        user = self.manager.get_by_natural_key(email.lower())
        self.assertEqual(user, existing_user)


class TestVerifyEmailMixin(TestCase):
    model = models.VerifyEmailUser

    def test_save(self):
        user = self.model()
        user.save()
        self.assertFalse(user.is_active)
        self.assertFalse(user.email_verified)

    def test_email_context(self):
        """Assert `password_reset_email_context` returns the correct data."""
        mocked_user = Mock()
        mocked_site = Mock()

        class DummyNotification:
            user = mocked_user
            site = mocked_site

        notification = DummyNotification()
        context = validation_email_context(notification)

        expected_context = {
            'protocol': 'https',
            'token': mocked_user.generate_validation_token(),
            'site': mocked_site,
        }
        self.assertEqual(context, expected_context)

    def test_send_validation_email(self):
        context = {}
        site = Site.objects.get_current()
        user = self.model(email='email@email.email')

        with patch(VALIDATION_CONTEXT) as get_context:
            get_context.return_value = context
            with patch(SEND_METHOD) as send:
                user.send_validation_email()

        expected = {
            'to': user.email,
            'template_name': 'user_management/account_validation_email.txt',
            'html_template_name': 'user_management/account_validation_email.html',
            'subject': '{} account validate'.format(site.domain),
            'context': context,
            'headers': {},
        }
        send.assert_called_once_with(**expected)

    def test_verified_email(self):
        user = self.model(email_verified=True)

        with patch(SEND_METHOD) as send:
            with self.assertRaises(ValueError):
                user.send_validation_email()

        self.assertFalse(send.called)

    def test_manager_check_valid(self):
        errors = self.model.check()
        self.assertEqual(errors, [])

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


class TestCustomNameUser(utils.APIRequestTestCase):
    model = models.CustomNameUser

    def test_fields(self):
        """Do we have the fields we expect?"""
        fields = {field.name for field in self.model._meta.get_fields()}
        expected = {
            # On model
            'id',
            'name',
            'date_joined',
            'email',
            'email_verified',
            'is_active',
            'is_staff',
            'last_login',
            'password',
            'avatar',
        }

        self.assertCountEqual(fields, expected)

    def test_name(self):
        expected = u'Cú Chulainn'
        model = self.model(name=expected)

        self.assertEqual(model.get_full_name(), expected)
        self.assertEqual(str(model), expected)
        field = self.model._meta.get_field('name')
        self.assertIsInstance(field, TextField)

    def test_manager_check_invalid(self):
        errors = self.model.check()
        self.assertEqual(errors, [])


class TestCustomPasswordResetNotification(TestCase):
    """Assert we can customise the notification to send a password reset."""
    model = models.CustomVerifyEmailUser

    def test_send_password_reset_email(self):
        """Assert `text_email_template` and `html_template_name` can be customised."""
        context = {}
        site = Site.objects.get_current()
        user = self.model(email='email@email.email')

        with patch(PASSWORD_CONTEXT) as get_context:
            get_context.return_value = context
            with patch(SEND_METHOD) as send:
                user.send_password_reset()

        expected = {
            'to': user.email,
            'template_name': 'my_custom_email.txt',
            'html_template_name': None,
            'subject': '{} password reset'.format(site.domain),
            'context': context,
            'headers': {'test-header': 'Test'},
        }
        send.assert_called_once_with(**expected)
