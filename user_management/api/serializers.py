import copy
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from imagekit.cachefiles import ImageCacheFile
from imagekit.registry import generator_registry
from imagekit.templatetags.imagekit import DEFAULT_THUMBNAIL_GENERATOR
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, label=_('Password'))
    password2 = serializers.CharField(write_only=True, min_length=8, label=_('Repeat password'))

    class Meta:
        fields = ['name', 'email', 'password', 'password2']
        model = User

    def validate_email(self, attrs, source):
        email = attrs.get('email')

        # Required check happens elsewhere, so no error if email is None
        if email is None:
            return attrs

        try:
            User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return attrs
        else:
            msg = _('That email address has already been registered.')
            raise serializers.ValidationError(msg)

    def validate_password2(self, attrs, source):
        password2 = attrs.pop(source)
        if password2 != attrs.get('password'):
            msg = _('Your passwords do not match.')
            raise serializers.ValidationError(msg)
        return attrs

    def restore_object(self, attrs, instance=None):
        password = attrs.pop('password')
        instance = super(RegistrationSerializer, self).restore_object(attrs, instance)
        instance.set_password(password)
        return instance


class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'new_password2')

    def restore_object(self, attrs, instance=None):
        instance = super(PasswordChangeSerializer, self).restore_object(attrs, instance)
        instance.set_password(attrs['new_password'])
        return instance

    def validate_old_password(self, attrs, source):
        value = attrs[source]
        if not self.object.check_password(value):
            msg = _('Invalid password.')
            raise serializers.ValidationError(msg)
        return attrs

    def validate_new_password2(self, attrs, source):
        if attrs['new_password'] != attrs[source]:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError(msg)
        return attrs


class PasswordResetSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('new_password', 'new_password2')

    def restore_object(self, attrs, instance=None):
        instance = super(PasswordResetSerializer, self).restore_object(attrs, instance)
        instance.set_password(attrs['new_password'])
        return instance

    def validate_new_password2(self, attrs, source):
        if attrs['new_password'] != attrs[source]:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError(msg)
        return attrs


class PasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=511)

    class Meta:
        fields = ['email']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'date_joined')
        read_only_fields = ('email', 'date_joined')


class HyperlinkedImageField(serializers.ImageField):
    """Image field that returns the images url."""
    def to_native(self, value):
        request = self.context.get('request', None)
        if value.name is None:
            return None
        url = value.url
        if request is not None:
            url = request.build_absolute_uri(value.url)
        return url


class AvatarSerializer(serializers.ModelSerializer):
    # Override default ImageField mapping to use HyperlinkedImageField
    field_mapping = copy.copy(serializers.ModelSerializer.field_mapping)
    field_mapping.update({
        models.ImageField: HyperlinkedImageField,
    })

    class Meta:
        model = User
        fields = ('avatar',)


class AvatarThumbnailSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField('get_thumbnail')

    class Meta:
        model = User
        fields = ('thumbnail',)

    def get_generator_kwargs(self, query_params):
        generator_id = query_params.get('generator', DEFAULT_THUMBNAIL_GENERATOR)
        width = int(query_params.get('width', 0)) or None
        height = int(query_params.get('height', 0)) or None
        return {
            'id': generator_id,
            'width': width,
            'height': height,
            'anchor': query_params.get('anchor', None),
            'crop': query_params.get('crop', None),
            'upscale': query_params.get('upscale', None)
        }

    def generate_thnumbnail(self, source, **kwargs):
        generator = generator_registry.get(source=source, **kwargs)
        return ImageCacheFile(generator, storage=source.storage)

    def get_thumbnail(self, obj):
        if obj.avatar.name is None:
            return None

        request = self.context.get('request', None)
        if request is None:
            return obj.avatar.url

        image = obj.avatar
        kwargs = self.get_generator_kwargs(request.QUERY_PARAMS)
        if kwargs.get('width') or kwargs.get('height'):
            image = self.generate_thnumbnail(image, **kwargs)

        return request.build_absolute_uri(image.url)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    def validate_email(self, attrs, source):
        email = attrs.get('email')

        # Required check happens elsewhere, so no error if email is None
        if email is None:
            return attrs

        qs = User.objects.all()
        if self.object and self.object.pk:
            qs = qs.exclude(pk=self.object.pk)

        try:
            qs.get(email__iexact=email)
        except User.DoesNotExist:
            return attrs
        else:
            msg = _('That email address is already in use.')
            raise serializers.ValidationError(msg)

    class Meta:
        model = User
        fields = ('url', 'name', 'email', 'date_joined')
        read_only_fields = ('email', 'date_joined')
        view_name = 'user_management_api:user_detail'


class UserSerializerCreate(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('date_joined',)
