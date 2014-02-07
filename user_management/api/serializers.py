from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
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
        instance = super().restore_object(attrs, instance)
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
        instance = super().restore_object(attrs, instance)
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
        instance = super().restore_object(attrs, instance)
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
        read_only_fields = ('email',)
