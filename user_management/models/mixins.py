from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core import checks
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
    email = models.EmailField(
        verbose_name=_('Email address'),
        unique=True,
        max_length=511,
    )
    email_verification_required = False

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
    EMAIL_SUBJECT = '{domain} account validate'
    TEXT_EMAIL_TEMPLATE = 'user_management/account_validation_email.txt'
    HTML_EMAIL_TEMPLATE = 'user_management/account_validation_email.html'

    def email_context(self, site):
        return {
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
            'site': site,
        }

    def email_kwargs(self, context, domain):
        """Prepare the kwargs to be passed to incuna_mail.send"""
        return {
            'to': [self.email],
            'template_name': self.TEXT_EMAIL_TEMPLATE,
            'html_template_name': self.HTML_EMAIL_TEMPLATE,
            'subject': self.get_email_subject(domain),
            'context': context,
        }

    def get_email_subject(self, domain):
        return _(self.EMAIL_SUBJECT).format(domain=domain)

    def send_validation_email(self):
        """
        Send a validation email to the user's email address.

        The email subject can be customised by overriding
        VerifyEmailMixin.EMAIL_SUBJECT or VerifyEmailMixin.get_email_subject.
        To include your site's domain in the subject, include {domain} in
        VerifyEmailMixin.EMAIL_SUBJECT.

        By default send_validation_email sends a multipart email using
        VerifyEmailMixin.TEXT_EMAIL_TEMPLATE and
        VerifyEmailMixin.HTML_EMAIL_TEMPLATE. To send a text-only email
        set VerifyEmailMixin.HTML_EMAIL_TEMPLATE to None.

        You can also customise the context available in the email templates
        by extending VerifyEmailMixin.email_context.

        If you want more control over the sending of the email you can
        extend VerifyEmailMixin.email_kwargs.
        """
        if not self.email_verification_required:
            raise ValueError(_('Cannot validate already active user.'))

        site = Site.objects.get_current()
        context = self.email_context(site)
        send(**self.email_kwargs(context, site.domain))


class EmailVerifyUserMixin(EmailVerifyUserMethodsMixin, models.Model):
    is_active = models.BooleanField(_('active'), default=False)
    email_verification_required = models.BooleanField(
        _('Email verification required?'),
        default=True,
        help_text=_('Indicates if the email address needs to be verified.'))

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
