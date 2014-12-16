from django.test import TestCase
from mock import MagicMock, patch

from user_management.models.tests.factories import UserFactory
from .. import serializers


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

        get_path = 'user_management.api.avatar.serializers.generator_registry.get'
        image_cache_path = 'user_management.api.avatar.serializers.ImageCacheFile'
        with patch(get_path) as get:
            get.return_value = generator
            with patch(image_cache_path) as ImageCacheFile:
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
