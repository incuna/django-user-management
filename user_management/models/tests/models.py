from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import (
    BasicUserFieldsMixin,
    VeryifyEmailMixin,
    VerifiedEmailManagerMixin,
    UserManager as BaseUserManager)


class UserManager(VerifiedEmailManagerMixin, BaseUserManager):
    pass


class User(BasicUserFieldsMixin, VeryifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    objects = UserManager()
