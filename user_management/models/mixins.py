from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send


class UserManager(BaseUserManager):
    """Django requires user managers to have create_user & create_superuser."""
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(
            email=email.lower(),
            date_joined=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.update({
            'is_staff': True,
            'is_superuser': True,
        })
        user = self.create_user(email, password, **extra_fields)
        return user


class BaseUserMixin(models.Model):
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


class IsActiveMixin(models.Model):
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        abstract = True


class VerifiedEmailManagerMixin(object):
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.update({
            'is_active': True,
        })
        user = super(VerifiedEmailManagerMixin, self).create_superuser(
            email,
            password,
            **extra_fields)
        return user


class VerifiedEmailManager(VerifiedEmailManagerMixin, BaseUserManager):
    pass


class VerifiedEmailMixin(models.Model):
    is_active = models.BooleanField(_('active'), default=False)
    verified_email = models.BooleanField(_('Verified email address'), default=False)

    objects = VerifiedEmailManager()

    class Meta:
        abstract = True

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
