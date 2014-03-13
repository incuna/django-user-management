from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from ..mixins import VerifyEmailMixin
from user_management.api.avatar.mixins import AvatarMixin


class User(AvatarMixin, VerifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass
