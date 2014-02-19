from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from ..mixins import VerifyEmailMixin, AvatarMixin


class User(AvatarMixin, VerifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass
