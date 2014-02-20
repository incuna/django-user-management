from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes, python_2_unicode_compatible
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send


class UserManager(BaseUserManager):
    """Django requires user managers to have create_user & create_superuser."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email address must be set')
        email = self.normalize_email(email).lower()
        user = self.model(
            email=email,
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


@python_2_unicode_compatible
class BasicUserFieldsMixin(models.Model):
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=255,
    )
    email = models.EmailField(
        verbose_name=_('Email address'),
        unique=True,
        max_length=511,
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
        editable=False,
    )
    is_staff = models.BooleanField(_('staff status'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name


class ActiveUserMixin(BasicUserFieldsMixin):
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


class VerifyEmailMixin(BasicUserFieldsMixin):
    is_active = models.BooleanField(_('active'), default=False)
    verified_email = models.BooleanField(_('Verified email address'),
        default=False,
        help_text=_('Indicates if the email address has been verified.'))

    objects = VerifyEmailManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(VerifyEmailMixin, self).save(*args, **kwargs)
        if not self.verified_email:
            self.send_validation_email()

    def send_validation_email(self):
        if self.verified_email:
            raise ValueError('Cannot validate already active user.')

        context = {
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
        }
        site = Site.objects.get_current()

        send(
            to=[self.email],
            template_name='user_management/account_validation_email.html',
            subject='{} account validate'.format(site.domain),
            extra_context=context,
        )


class AvatarMixin(models.Model):
    avatar = models.ImageField(upload_to='user_avatar', blank=True)

    class Meta:
        abstract = True
