from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from user_management.utils.validators import validate_password_strength


User = get_user_model()


class ValidateEmailMixin(object):
    def validate_email(self, attrs, source):
        email = attrs.get(source).lower()

        try:
            User.objects.get_by_natural_key(email)
        except User.DoesNotExist:
            attrs[source] = email
            return attrs
        else:
            msg = _('That email address has already been registered.')
            raise serializers.ValidationError(msg)


class EmailSerializerBase(serializers.Serializer):
    """Serializer defining a read-only `email` field."""
    email = serializers.EmailField(max_length=511, label=_('Email address'))

    class Meta:
        fields = ['email']


class RegistrationSerializer(ValidateEmailMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('Password'),
        validators=[validate_password_strength],
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('Repeat password'),
    )

    class Meta:
        fields = ['name', 'email', 'password', 'password2']
        model = User

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        if password2 != attrs.get('password'):
            msg = _('Your passwords do not match.')
            raise serializers.ValidationError({'password2': [msg]})
        return attrs

    def restore_object(self, attrs, instance=None):
        password = attrs.pop('password')
        instance = super(RegistrationSerializer, self).restore_object(attrs, instance)
        instance.set_password(password)
        return instance


class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(
        write_only=True,
        label=_('Old password'),
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('New password'),
        validators=[validate_password_strength],
    )
    new_password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('Repeat new password'),
    )

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'new_password2')

    def restore_object(self, attrs, instance=None):
        instance = super(PasswordChangeSerializer, self).restore_object(
            attrs,
            instance,
        )
        instance.set_password(attrs['new_password'])
        return instance

    def validate_old_password(self, attrs, source):
        value = attrs[source]
        if not self.object.check_password(value):
            msg = _('Invalid password.')
            raise serializers.ValidationError(msg)
        return attrs

    def validate(self, attrs):
        if attrs.get('old_password') == attrs.get('new_password'):
            msg = _('Your new password must not be the same as your old password.')
            raise serializers.ValidationError({'new_password': [msg]})
        if attrs.get('new_password') != attrs['new_password2']:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError({'new_password2': [msg]})
        return attrs


class PasswordResetSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('New password'),
        validators=[validate_password_strength],
    )
    new_password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        label=_('Repeat new password'),
    )

    class Meta:
        model = User
        fields = ('new_password', 'new_password2')

    def restore_object(self, attrs, instance=None):
        instance = super(PasswordResetSerializer, self).restore_object(
            attrs,
            instance,
        )
        instance.set_password(attrs['new_password'])
        return instance

    def validate(self, attrs):
        if attrs.get('new_password') != attrs['new_password2']:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError({'new_password2': [msg]})
        return attrs


class PasswordResetEmailSerializer(EmailSerializerBase):
    """Serializer defining an `email` field to reset password."""


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'date_joined')
        read_only_fields = ('email', 'date_joined')


class ResendConfirmationEmailSerializer(EmailSerializerBase):
    """Serializer defining an `email` field to resend a confirmation email."""
    def validate_email(self, attrs, source):
        """Validate if email exists and requires a verification.

        `validate_email` will set a `user` attribute on the instance allowing
        the view to send an email confirmation."""
        email = attrs[source]
        try:
            self.user = User.objects.get_by_natural_key(email)
        except User.DoesNotExist:
            msg = _('A user with this email address does not exist.')
            raise serializers.ValidationError(msg)

        if not self.user.email_verification_required:
            msg = _('User email address is already verified.')
            raise serializers.ValidationError(msg)
        return attrs


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'name', 'email', 'date_joined')
        read_only_fields = ('email', 'date_joined')
        view_name = 'user_management_api:user_detail'


class UserSerializerCreate(ValidateEmailMixin, UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('date_joined',)
