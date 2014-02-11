from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import VerifyEmailMixin


class User(VerifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass
