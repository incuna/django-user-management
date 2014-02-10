from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import (
    VeryifyEmailMixin,
    VeryifyEmailManagerMixin,
    UserManager as BaseUserManager)


class UserManager(VeryifyEmailManagerMixin, BaseUserManager):
    pass


class User(VeryifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    objects = UserManager()
