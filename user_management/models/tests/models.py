from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import (
    BaseUserMixin,
    VerifiedEmailMixin,
    VerifiedEmailManagerMixin,
    UserManager as BaseUserManager)


class UserManager(VerifiedEmailManagerMixin, BaseUserManager):
    pass


class User(BaseUserMixin, VerifiedEmailMixin, PermissionsMixin, AbstractBaseUser):
    objects = UserManager()
