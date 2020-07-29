from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, validators

from user_management.utils.validators import validate_password_strength


User = get_user_model()


class UniqueEmailValidator(validators.UniqueValidator):
    def filter_queryset(self, value, queryset):
        """Check lower-cased email is unique."""
        return super(UniqueEmailValidator, self).filter_queryset(
            value.lower(),
            queryset,
        )


unique_email_validator = UniqueEmailValidator(
    queryset=User.objects.all(),
    message=_('That email address has already been registered.'),
)


class ValidateEmailMixin(object):
    def validate_email(self, value):
        return value.lower()


class EmailSerializerBase(serializers.Serializer):
    """Serializer defining a read-only `email` field."""
    email = serializers.EmailField(max_length=511, label=_('Email address'))

    class Meta:
        fields = ('email',)


class RegistrationSerializer(ValidateEmailMixin, serializers.ModelSerializer):
    email = serializers.EmailField(
        label=_('Email address'),
        validators=[unique_email_validator],
    )
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
        fields = ('name', 'email', 'password', 'password2')
        model = User

    def validate(self, attrs):
        password2 = attrs.pop('password2')
        if password2 != attrs.get('password'):
            msg = _('Your passwords do not match.')
            raise serializers.ValidationError({'password2': msg})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = self.Meta.model.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


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

    def update(self, instance, validated_data):
        """Check the old password is valid and set the new password."""
        if not instance.check_password(validated_data['old_password']):
            msg = _('Invalid password.')
            raise serializers.ValidationError({'old_password': msg})

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    def validate(self, attrs):
        if attrs.get('new_password') != attrs['new_password2']:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError({'new_password2': msg})
        if attrs.get('old_password') == attrs.get('new_password'):
            msg = _('Your new password must not be the same as your old password.')
            raise serializers.ValidationError({'new_password': msg})
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

    def update(self, instance, validated_data):
        """Set the new password for the user."""
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    def validate(self, attrs):
        if attrs.get('new_password') != attrs['new_password2']:
            msg = _('Your new passwords do not match.')
            raise serializers.ValidationError({'new_password2': msg})
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
    def validate_email(self, email):
        """
        Validate if email exists and requires a verification.

        `validate_email` will set a `user` attribute on the instance allowing
        the view to send an email confirmation.
        """
        try:
            self.user = User.objects.get_by_natural_key(email)
        except User.DoesNotExist:
            msg = _('A user with this email address does not exist.')
            raise serializers.ValidationError(msg)

        if self.user.email_verified:
            msg = _('User email address is already verified.')
            raise serializers.ValidationError(msg)
        return email


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'name', 'email', 'date_joined')
        read_only_fields = ('email', 'date_joined')
        extra_kwargs = {
            'url': {
                'lookup_field': 'pk',
                'view_name': 'user_management_api_users:user_detail',
            }
        }


class UserSerializerCreate(ValidateEmailMixin, UserSerializer):
    email = serializers.EmailField(
        label=_('Email address'),
        validators=[unique_email_validator],
    )

    class Meta(UserSerializer.Meta):
        read_only_fields = ('date_joined',)
