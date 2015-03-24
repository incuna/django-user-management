# Installation

## Dependencies

    djangorestframework
    incuna_mail

## Install with pip

Install the package:

    pip install django-user-management

Install with avatar functionality:

    pip install django-user-management[avatar]

Install with filtering sensitive data out of Sentry:

    pip install django-user-management[utils]


## User model

To create a custom user model using the `django-user-management` functionality, declare
your user class like this:

    from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
    from user_management.models.mixins import ActiveUserMixin


    class User(ActiveUserMixin, PermissionsMixin, AbstractBaseUser):
        pass

If you want to use the `VerifyEmailMixin`, substitute it for `ActiveUserMixin`.

Make sure the app containing your custom user model is added to `settings.INSTALLED_APPS`,
and set `settings.AUTH_USER_MODEL` to be the path to your custom user model.
