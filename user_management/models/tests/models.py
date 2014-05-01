from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from ..mixins import AvatarMixin, BasicUserFieldsMixin, VerifyEmailMixin


class User(AvatarMixin, VerifyEmailMixin, PermissionsMixin, AbstractBaseUser):
    pass


class BasicUser(BasicUserFieldsMixin, AbstractBaseUser):
    pass


class VerifyEmailUser(VerifyEmailMixin):
    pass
