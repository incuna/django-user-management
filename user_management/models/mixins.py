from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.postgres.fields import CIEmailField
from django.contrib.sites.models import Site
from django.core import checks, signing
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes, python_2_unicode_compatible
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from user_management.utils import notifications


class UserManager(BaseUserManager):
    """Django requires user managers to have create_user & create_superuser."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The given email address must be set'))
        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
            last_login=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        fields = {
            'is_staff': True,
            'is_superuser': True,
        }
        fields.update(extra_fields)
        user = self.create_user(email, password, **fields)
        return user

    def get_by_natural_key(self, email):
        """Get user by email with case-insensitive exact match.

        `get_by_natural_key` is used to `authenticate` a user, see:
        https://github.com/django/django/blob/c5780adeecfbd85a80b5aa7130dd86e78b23e497/django/contrib/auth/backends.py#L16
        """
        return self.get(email__iexact=email)


class DateJoinedUserMixin(models.Model):
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
        editable=False,
    )

    class Meta:
        abstract = True


class EmailUserMixin(models.Model):
    email = CIEmailField(
        verbose_name=_('Email address'),
        unique=True,
        max_length=511,
    )
    email_verified = True

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        abstract = True


class IsStaffUserMixin(models.Model):
    is_staff = models.BooleanField(_('staff status'), default=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class NameUserMethodsMixin:
    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def __str__(self):
        return self.name


class NameUserMixin(NameUserMethodsMixin, models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
    )
    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True
        ordering = ['name']


class BasicUserFieldsMixin(
        DateJoinedUserMixin, EmailUserMixin, IsStaffUserMixin, NameUserMixin):
    class Meta:
        abstract = True


class ActiveUserMixin(models.Model):
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        abstract = True


class VerifyEmailManager(UserManager):
    def create_superuser(self, email, password, **extra_fields):
        fields = {
            'is_active': True,
        }
        fields.update(extra_fields)
        user = super(VerifyEmailManager, self).create_superuser(
            email,
            password,
            **fields)
        return user


class EmailVerifyUserMethodsMixin:
    """
    Define how validation and password reset emails are sent.

    `password_reset_notification` and `validation_notification` can be overriden to
    provide custom settings to send emails.
    """
    password_reset_notification = notifications.PasswordResetNotification
    validation_notification = notifications.ValidationNotification

    def generate_validation_token(self):
        """Generate user token for account validation."""
        data = {'email': self.email}
        return signing.dumps(data)

    def generate_token(self):
        """Generate user token for password reset."""
        return default_token_generator.make_token(self)

    def generate_uid(self):
        """Generate user uid for password reset."""
        return urlsafe_base64_encode(force_bytes(self.pk))

    def send_validation_email(self):
        """Send a validation email to the user's email address."""
        if self.email_verified:
            raise ValueError(_('Cannot validate already active user.'))

        site = Site.objects.get_current()
        self.validation_notification(user=self, site=site).notify()

    def send_password_reset(self):
        """Send a password reset to the user's email address."""
        site = Site.objects.get_current()
        self.password_reset_notification(user=self, site=site).notify()


class EmailVerifyUserMixin(EmailVerifyUserMethodsMixin, models.Model):
    is_active = models.BooleanField(_('active'), default=False)
    email_verified = models.BooleanField(
        _('Email verified?'),
        default=False,
        help_text=_('Indicates if the email address has been verified.'))

    objects = VerifyEmailManager()

    class Meta:
        abstract = True

    @classmethod
    def check(cls, **kwargs):
        errors = super(EmailVerifyUserMixin, cls).check(**kwargs)
        errors.extend(cls._check_manager(**kwargs))
        return errors

    @classmethod
    def _check_manager(cls, **kwargs):
        if isinstance(cls.objects, VerifyEmailManager):
            return []

        return [
            checks.Warning(
                "Manager should be an instance of 'VerifyEmailManager'",
                hint="Subclass a custom manager from 'VerifyEmailManager'",
                obj=cls,
                id='user_management.W001',
            ),
        ]


class VerifyEmailMixin(EmailVerifyUserMixin, BasicUserFieldsMixin):
    class Meta:
        abstract = True


class AvatarMixin(models.Model):
    avatar = models.ImageField(upload_to='user_avatar', null=True, blank=True)

    class Meta:
        abstract = True
