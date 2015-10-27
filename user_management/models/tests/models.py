from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


from .notifications import CustomPasswordResetNotification
from ..mixins import (
    AvatarMixin,
    BasicUserFieldsMixin,
    DateJoinedUserMixin,
    EmailUserMixin,
    EmailVerifyUserMixin,
    IsStaffUserMixin,
    NameUserMethodsMixin,
    TimeZoneMixin,
    VerifyEmailMixin,
)


class User(
        AvatarMixin, TimeZoneMixin, VerifyEmailMixin, PermissionsMixin,
        AbstractBaseUser):
    """A User model using all the custom mixins."""


class BasicUser(BasicUserFieldsMixin, AbstractBaseUser):
    """A User model using just the BasicUserFieldsMixin."""


class VerifyEmailUser(VerifyEmailMixin, AbstractBaseUser):
    """A User model using just the VerifyEmailMixin."""


class CustomVerifyEmailUser(VerifyEmailMixin, AbstractBaseUser):
    """Customise the notification class to send a password reset."""
    password_reset_notification = CustomPasswordResetNotification


class CustomBasicUserFieldsMixin(
        NameUserMethodsMixin, EmailUserMixin, DateJoinedUserMixin,
        IsStaffUserMixin):
    """
    A replacement for BasicUserFieldsMixin with a custom name field.

    Uses NameUserMethodsMixin instead of NameUserMixin.
    """

    name = models.TextField()

    USERNAME_FIELD = 'email'

    class Meta:
        abstract = True


class CustomNameUser(
        AvatarMixin, EmailVerifyUserMixin, CustomBasicUserFieldsMixin,
        AbstractBaseUser):
    """A User model using the CustomBasicUserFieldsMixin."""
