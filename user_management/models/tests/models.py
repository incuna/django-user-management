from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import VeryifyEmailMixin


class User(VeryifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass
