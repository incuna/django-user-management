# Installation

## Dependencies

    djangorestframework
    incuna_mail

## Install with pip

Install the package

    pip install django-user-management

Install with avatar functionality

    pip install django-user-management[avatar]

Install with filtering sensitive data out of Sentry

    pip install django-user-management[utils]


## User model

Create a custom user model

    from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
    from user_management.models.mixins import ActiveUserMixin


    class User(ActiveUserMixin, PermissionsMixin, AbstractBaseUser):
        pass

If you want to use the `VerifyEmailMixin` then substitute it for `ActiveUserMixin`


Make sure your custom user model in added to `INSTALLED_APPS` and set 
`AUTH_USER_MODEL` to your custom user model.
