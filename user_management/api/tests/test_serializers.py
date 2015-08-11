# -*- coding: utf-8 -*-
import string

from django.test import TestCase
from rest_framework.fields import Field
from rest_framework.reverse import reverse
from rest_framework.serializers import ValidationError

from user_management.models.tests.factories import UserFactory
from user_management.models.tests.utils import RequestTestCase
from user_management.tests.utils import iso_8601
from .. import serializers


class ProfileSerializerTest(TestCase):
    def test_serialize(self):
        user = UserFactory.build()
        serializer = serializers.ProfileSerializer(user)

        expected = {
            'name': user.name,
            'email': user.email,
            'date_joined': iso_8601(user.date_joined),
        }
        self.assertEqual(serializer.data, expected)

    def test_deserialize(self):
        user = UserFactory.build()
        data = {
            'name': 'New Name',
        }
        serializer = serializers.ProfileSerializer(user, data=data)
        self.assertTrue(serializer.is_valid())


class PasswordChangeSerializerTest(TestCase):
    def test_deserialize_passwords(self):
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'

        user = UserFactory.create(password=old_password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_deserialize_invalid_old_password(self):
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'

        user = UserFactory.build(password=old_password)

        serializer = serializers.PasswordChangeSerializer()
        data = {
            'old_password': 'invalid_password',
            'new_password': new_password,
            'new_password2': new_password,
        }
        with self.assertRaises(ValidationError):
            serializer.update(user, data)

    def test_deserialize_invalid_new_password(self):
        old_password = '0ld_passworD'
        new_password = '2Short'

        user = UserFactory.build(password=old_password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)

    def test_deserialize_mismatched_passwords(self):
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'
        other_password = 'other_new_password'

        user = UserFactory.create(password=old_password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': other_password,
        })
        self.assertFalse(serializer.is_valid())

    def test_no_change_password(self):
        """A password cannot be changed if it doesn't change!"""
        password = 'Same_passw0rd'

        user = UserFactory.create(password=password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': password,
            'new_password': password,
            'new_password2': password,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)


class PasswordResetSerializerTest(TestCase):
    def test_deserialize_passwords(self):
        new_password = 'n3w_Password'
        user = UserFactory.create()

        serializer = serializers.PasswordResetSerializer(user, data={
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_deserialize_invalid_new_password(self):
        new_password = '2Short'
        user = UserFactory.build()

        serializer = serializers.PasswordResetSerializer(user, data={
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)

    def test_deserialize_mismatched_passwords(self):
        new_password = 'n3w_Password'
        other_password = 'other_new_password'
        user = UserFactory.create()

        serializer = serializers.PasswordResetSerializer(user, data={
            'new_password': new_password,
            'new_password2': other_password,
        })
        self.assertFalse(serializer.is_valid())


class RegistrationSerializerTest(TestCase):
    def setUp(self):
        super(RegistrationSerializerTest, self).setUp()
        self.data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': 'Bobby.Tables+327@xkcd.com',
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }

    def test_deserialize(self):
        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        validated_data = serializer.validated_data
        self.assertEqual(validated_data['name'], self.data['name'])
        self.assertEqual(validated_data['email'], self.data['email'].lower())
        self.assertEqual(validated_data['password'], self.data['password'])

    def test_deserialize_invalid_new_password(self):
        self.data['password'] = '2short'

        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_deserialize_mismatched_passwords(self):
        self.data['password2'] = 'different_password'
        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)

    def test_deserialize_no_email(self):
        self.data['email'] = None

        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)


class UserSerializerTest(RequestTestCase):
    def test_serialize(self):
        user = UserFactory.create()
        request = self.create_request()
        context = {'request': request}
        serializer = serializers.UserSerializer(user, context=context)

        url = reverse(
            'user_management_api:user_detail',
            kwargs={'pk': user.pk},
            request=request,
        )

        expected = {
            'url': url,
            'name': user.name,
            'email': user.email,
            'date_joined': iso_8601(user.date_joined),
        }
        self.assertEqual(serializer.data, expected)

    def test_deserialize(self):
        user = UserFactory.build()
        data = {
            'name': 'New Name',
        }
        serializer = serializers.UserSerializer(user, data=data)
        self.assertTrue(serializer.is_valid())

    def test_deserialize_create_email_in_use(self):
        other_user = UserFactory.create()
        data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': other_user.email,
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }
        serializer = serializers.RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer._errors['email'],
            ['That email address has already been registered.'])

    def test_deserialize_update_email_in_use(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': other_user.email,
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }
        serializer = serializers.RegistrationSerializer(user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer._errors['email'],
            ['That email address has already been registered.'])


class TestUserSerializerCreate(TestCase):
    def test_deserialize_no_email(self):
        data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': None,
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }

        serializer = serializers.UserSerializerCreate(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_deserialize_email_in_use(self):
        other_user = UserFactory.create()
        data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': other_user.email,
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }
        serializer = serializers.UserSerializerCreate(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer._errors['email'],
            ['That email address has already been registered.'],
        )


class SerializerPasswordsTest(TestCase):
    too_simple = (
        'Password must have at least ' +
        'one upper case letter, one lower case letter, and one number.'
    )

    too_fancy = (
        'Password only accepts the following symbols ' + string.punctuation
    )

    serializers = (
        (serializers.PasswordResetSerializer, 'new_password'),
        (serializers.PasswordChangeSerializer, 'new_password'),
        (serializers.RegistrationSerializer, 'password'),
    )

    def assert_validation_error(self, serializer_class, field, data, expected):
        serializer = serializer_class(data=data)
        serializer.is_valid()  # Perform validation
        on_missing = '{} not in {}.errors'.format(field, serializer)
        self.assertTrue(field in serializer.errors, on_missing)
        error = serializer.errors[field]
        on_wrong = 'Expected "{}", got "{}" on {}'.format(
            expected,
            error,
            serializer,
        )
        self.assertEqual(error, [expected], on_wrong)

    def assert_no_validation_error(self, serializer_class, field, data):
        serializer = serializer_class(data=data)
        serializer.is_valid()  # Perform validation
        on_present = '{} unexpectedly in {}.errors'.format(field, serializer)
        self.assertFalse(field in serializer.errors, on_present)

    def test_missing(self):
        data = {}
        for serializer_class, field in self.serializers:
            msg = Field.default_error_messages['required']
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_too_short(self):
        for serializer_class, field in self.serializers:
            data = {field: 'Aa1'}
            msg = 'Ensure this field has at least 8 characters.'
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_no_upper(self):
        for serializer_class, field in self.serializers:
            data = {field: 'aaaa1111'}
            msg = self.too_simple
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_no_lower(self):
        for serializer_class, field in self.serializers:
            data = {field: 'AAAA1111'}
            msg = self.too_simple
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_no_number(self):
        for serializer_class, field in self.serializers:
            data = {field: 'AAAAaaaa'}
            msg = self.too_simple
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_symbols(self):
        """Ensure all acceptable symbols are acceptable."""
        for serializer_class, field in self.serializers:
            for symbol in string.punctuation:
                data = {field: 'AAaa111' + symbol}
                self.assert_no_validation_error(serializer_class, field, data)

    def test_non_ascii(self):
        for serializer_class, field in self.serializers:
            data = {field: u'AA11aa££'}  # £ is not an ASCII character.
            msg = self.too_fancy
            self.assert_validation_error(serializer_class, field, data, msg)

    def test_ok(self):
        for serializer_class, field in self.serializers:
            data = {field: 'AAAaaa11'}
            self.assert_no_validation_error(serializer_class, field, data)


class ResendConfirmationEmailSerializerTest(TestCase):
    def test_serialize(self):
        """Assert user can request a new email confirmation."""
        user = UserFactory.create()
        data = {'email': user.email}
        serializer = serializers.ResendConfirmationEmailSerializer(data=data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)

    def test_user_does_not_exist(self):
        """Assert user should exist before sending email confirmation."""
        data = {'email': 'a-non-existing@user.com'}
        serializer = serializers.ResendConfirmationEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_user_already_validated(self):
        """Assert confirmation email is not send if user was already verified."""
        user = UserFactory.create(email_verified=True)
        data = {'email': user.email}
        serializer = serializers.ResendConfirmationEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())
