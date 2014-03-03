from django.core.urlresolvers import reverse
from django.test import TestCase
from mock import patch, MagicMock

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


class AvatarSerializerTest(TestCase):
    def test_deserialize(self):
        user = UserFactory.build()
        data = {'avatar': ''}
        serializer = serializers.AvatarSerializer(user, data=data)
        self.assertTrue(serializer.is_valid())


class ThumbnailField(TestCase):
    def test_get_generator_kwargs(self):
        expected = {
            'width': 50,
            'height': 50,
            'anchor': 'tr',
            'crop': 1,
            'upscale': 1,
        }
        field = serializers.ThumbnailField()
        kwargs = field.get_generator_kwargs(expected)
        self.assertEqual(kwargs, expected)

    def test_get_generator_kwargs_defaults(self):
        expected = {
            'width': None,
            'height': None,
            'anchor': None,
            'crop': None,
            'upscale': None,
        }
        field = serializers.ThumbnailField()
        kwargs = field.get_generator_kwargs({})
        self.assertEqual(kwargs, expected)

    def test_get_generator_kwargs_limited(self):
        expected = {
            'width': None,
            'height': None,
            'anchor': None,
            'crop': None,
            'upscale': None,
        }
        field = serializers.ThumbnailField()
        kwargs = field.get_generator_kwargs({'ignored': 'value'})
        self.assertEqual(kwargs, expected)

    def test_generate_thumbnail(self):
        field = serializers.ThumbnailField()
        source = 'test'
        kwargs = {'width': 10}
        generator = 'generator'
        with patch('user_management.api.serializers.generator_registry.get') as get:
            get.return_value = generator
            with patch('user_management.api.serializers.ImageCacheFile') as ImageCacheFile:
                field.generate_thumbnail(source, **kwargs)

        get.assert_called_once_with(field.generator_id, source=source, **kwargs)
        ImageCacheFile.assert_called_once_with(generator)

    def test_to_native_no_image(self):
        """Calling to_native with empty image should return None."""
        field = serializers.ThumbnailField()
        mocked_image = MagicMock()
        mocked_image.name = None
        image = field.to_native(mocked_image)
        self.assertEqual(image, None)

    def test_to_native_no_request(self):
        """Calling to_native with no request returns the image url."""
        field = serializers.ThumbnailField()
        field.context = {'request': None}
        expected = '/url/'
        mocked_image = MagicMock(
            name='image.png',
            url=expected
        )
        image = field.to_native(mocked_image)
        self.assertEqual(image, expected)

    def test_to_native_no_kwargs(self):
        """Calling to_native with no QUERY_PARAMS returns the absolute image url."""
        field = serializers.ThumbnailField()
        request = MagicMock()
        expected = 'test.com/url/'
        request.build_absolute_uri.return_value = expected

        field.context = {'request': request}
        field.get_generator_kwargs = MagicMock(return_value={})
        mocked_image = MagicMock(
            name='image.png',
            url='/anything/'
        )
        image = field.to_native(mocked_image)
        self.assertEqual(image, expected)
        request.build_absolute_uri.assert_called_once_with(mocked_image.url)

    def test_to_native_calls_generate_thumbnail(self):
        """Calling to_native with QUERY_PARAMS calls generate_thumbnail."""
        field = serializers.ThumbnailField()

        request = MagicMock()
        field.context = {'request': request}

        kwargs = {'width': 100}
        field.get_generator_kwargs = MagicMock(return_value=kwargs)

        thumbnailed_image = MagicMock(
            url='/thumbnail/'
        )
        field.generate_thumbnail = MagicMock(return_value=thumbnailed_image)

        expected = 'test.com/url/'
        request.build_absolute_uri.return_value = expected

        mocked_image = MagicMock(
            name='image.png',
            url='/anything/'
        )
        image = field.to_native(mocked_image)
        self.assertEqual(image, expected)
        field.generate_thumbnail.assert_called_once_with(mocked_image, **kwargs)
        request.build_absolute_uri.assert_called_once_with(thumbnailed_image.url)


class UserSerializerTest(TestCase):
    def test_serialize(self):
        user = UserFactory.create()
        serializer = serializers.UserSerializer(user)

        url = reverse('user_management_api:user_detail', kwargs={'pk': user.pk})

        expected = {
            'url': url,
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
