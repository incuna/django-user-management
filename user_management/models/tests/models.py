from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


from ..mixins import (
    AvatarMixin,
    BasicUserFieldsMixin,
    DateJoinedUserMixin,
    EmailUserMixin,
    EmailVerifyUserMixin,
    IsStaffUserMixin,
    NameUserMethodsMixin,
    VerifyEmailMixin,
)


class User(AvatarMixin, VerifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass


class BasicUser(BasicUserFieldsMixin, AbstractBaseUser):
    pass


class VerifyEmailUser(VerifyEmailMixin):
    pass


class CustomBasicUserFieldsMixin(
        NameUserMethodsMixin, EmailUserMixin, DateJoinedUserMixin,
        IsStaffUserMixin):
    name = models.TextField()

    USERNAME_FIELD = 'email'

    class Meta:
        abstract = True


class CustomNameUser(
        AvatarMixin, EmailVerifyUserMixin, CustomBasicUserFieldsMixin,
        AbstractBaseUser):
    pass
