from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import (
    VeryifyEmailMixin,
    VerifiedEmailManagerMixin,
    UserManager as BaseUserManager)


class UserManager(VerifiedEmailManagerMixin, BaseUserManager):
    pass


class User(VeryifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    objects = UserManager()
