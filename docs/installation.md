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

If you use `EmailUserMixin` or any of its derivatives, you'll need to set up Postgres to support a `CIText` extension in your migration. Add the following to your migration:

    from django.contrib.postgres.operations import CITextExtension
	
    operations = [
        CITextExtension(),
        ...
    ]

## Authtoken

If you have `user_management.api` in your `INSTALLED_APPS`, you'll also need to create a migration in your project for the `AuthToken` model.

Add the following to `settings.MIGRATION_MODULES`:

    MIGRATION_MODULES = {
        ...
        'api': 'core.projectmigrations.user_management_api',  # substitute the path to your projectmigrations folder
        ...
    }

Then run `python manage.py makemigrations api` to create the migration you need.  This avoids database errors involving the relation `users_user` not existing when Django tries to synchronise the "unmigrated" `api` app before setting up the rest of the database.
