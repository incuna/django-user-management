# django-user-management [![Build Status](https://travis-ci.org/incuna/django-user-management.png?branch=merge-version)](https://travis-ci.org/incuna/django-user-management)

User management model mixins and api views.

## Custom user model mixins

###  ActiveUserMixin
`user_management.models.mixins.ActiveUserMixin` provides a base custom user
mixin with a `name`, `email`, `date_joined`, `is_staff`, and `is_active`.

###  VerifyEmailMixin
`user_management.models.mixins.VerifyEmailMixin` extends ActiveUserMixin to
provide functionality to verify the email. It includes an additional
`verified_email` field.  
By default users will be created with `is_active = False`, a verification email
will be sent including a link to verify the email and activate the account. 


## Installation
Install the package

    pip install django-user-management


Create a custom user model

    from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
    from user_management.models.mixins import ActiveUserMixin


    class User(ActiveUserMixin, PermissionsMixin, AbstractBaseUser):
        pass

If you want to use the `VerifyEmailMixin` then substitute it for `ActiveUserMixin`


Make sure your custom user model in added to `INSTALLED_APPS` and set 
`AUTH_USER_MODEL` to your custom user model.


### To use the api views
Add to your `INSTALLED_APPS` in `settings.py`

    INSTALLED_APPS = (
        ...
        'user_management.api',
        ...
    )

Add the urls to your `ROOT_URLCONF`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.urls')),
        ...
    )

If you are using the `VerifyEmailMixin` then replace `user_management.api.url`
with `user_management.api.verify_email_urls`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.verify_email_urls')),
        ...
    )
