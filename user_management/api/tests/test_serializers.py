from django.test import TestCase

from .. import serializers
from user_management.models.tests.factories import UserFactory


class ProfileSerializerTest(TestCase):
    def test_serialize(self):
        user = UserFactory.build()
        serializer = serializers.ProfileSerializer(user)

        expected = {
            'name': user.name,
            'email': user.email,
            'date_joined': user.date_joined,
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
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_deserialize_invalid_old_password(self):
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.build()
        user.set_password(old_password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': 'invalid_password',
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)

    def test_deserialize_invalid_new_password(self):
        old_password = 'old_password'
        new_password = '2short'

        user = UserFactory.build()
        user.set_password(old_password)

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
        self.assertTrue(serializer.object.check_password(old_password))

    def test_deserialize_mismatched_passwords(self):
        old_password = 'old_password'
        new_password = 'new_password'
        other_password = 'other_new_password'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        serializer = serializers.PasswordChangeSerializer(user, data={
            'old_password': old_password,
            'new_password': new_password,
            'new_password2': other_password,
        })
        self.assertFalse(serializer.is_valid())


class PasswordResetSerializerTest(TestCase):
    def test_deserialize_passwords(self):
        new_password = 'new_password'
        user = UserFactory.create()

        serializer = serializers.PasswordResetSerializer(user, data={
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertTrue(user.check_password(new_password))

    def test_deserialize_invalid_new_password(self):
        new_password = '2short'
        user = UserFactory.build()

        serializer = serializers.PasswordResetSerializer(user, data={
            'new_password': new_password,
            'new_password2': new_password,
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password', serializer.errors)
        self.assertFalse(serializer.object.check_password(new_password))

    def test_deserialize_mismatched_passwords(self):
        new_password = 'new_password'
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
            'email': 'bobby.tables+327@xkcd.com',
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }

    def test_deserialize(self):
        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        user = serializer.object
        self.assertEqual(user.name, self.data['name'])
        self.assertTrue(user.check_password(self.data['password']))

    def test_deserialize_invalid_new_password(self):
        self.data['password'] = '2short'

        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertIs(serializer.object, None)

    def test_deserialize_mismatched_passwords(self):
        self.data['password2'] = 'different_password'
        serializer = serializers.RegistrationSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)
