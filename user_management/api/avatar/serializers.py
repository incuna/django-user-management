from django.contrib.auth import get_user_model
from django.db import models
from imagekit.cachefiles import ImageCacheFile
from imagekit.registry import generator_registry
from imagekit.templatetags.imagekit import DEFAULT_THUMBNAIL_GENERATOR
from rest_framework import serializers

User = get_user_model()


class ThumbnailField(serializers.ImageField):
    """
    Image field that returns an images url.
    Pass get parameters to thumbnail the image.
    Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    If no options are specified the users avatar is returned.

    To crop to 100x100 anchored to the top right:
        ?width=100&height=100&crop=1&anchor=tr
    """
    def __init__(self, *args, **kwargs):
        self.generator_id = kwargs.pop('generator_id', DEFAULT_THUMBNAIL_GENERATOR)
        super(ThumbnailField, self).__init__(*args, **kwargs)

    def get_generator_kwargs(self, query_params):
        width = int(query_params.get('width', 0)) or None
        height = int(query_params.get('height', 0)) or None
        return {
            'width': width,
            'height': height,
            'anchor': query_params.get('anchor', None),
            'crop': query_params.get('crop', None),
            'upscale': query_params.get('upscale', None)
        }

    def generate_thumbnail(self, source, **kwargs):
        generator = generator_registry.get(
            self.generator_id,
            source=source,
            **kwargs)
        return ImageCacheFile(generator)

    def to_native(self, image):
        if not image.name:
            return None

        request = self.context.get('request', None)
        if request is None:
            return image.url

        kwargs = self.get_generator_kwargs(request.query_params)
        if kwargs.get('width') or kwargs.get('height'):
            image = self.generate_thumbnail(image, **kwargs)

        return request.build_absolute_uri(image.url)


class AvatarSerializer(serializers.ModelSerializer):
    # Override default field_mapping to map ImageField to HyperlinkedImageField.
    # As there is only one field this is the only mapping needed.
    field_mapping = {
        models.ImageField: ThumbnailField,
    }

    class Meta:
        model = User
        fields = ('avatar',)
