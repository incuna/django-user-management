# django-user-management [![Build Status](https://travis-ci.org/incuna/django-user-management.png?branch=merge-version)](https://travis-ci.org/incuna/django-user-management) [![Coverage Status](https://coveralls.io/repos/incuna/django-user-management/badge.png?branch=master)](https://coveralls.io/r/incuna/django-user-management?branch=master) [![Requirements Status](https://requires.io/github/incuna/django-user-management/requirements.svg?branch=master)](https://requires.io/github/incuna/django-user-management/requirements/?branch=master)

User management model mixins and api views.

## Custom user model mixins

###  ActiveUserMixin
`user_management.models.mixins.ActiveUserMixin` provides a base custom user
mixin with a `name`, `email`, `date_joined`, `is_staff`, and `is_active`.

###  VerifyEmailMixin
`user_management.models.mixins.VerifyEmailMixin` extends ActiveUserMixin to
provide functionality to verify the email. It includes an additional
`email_verification_required` field.  
By default users will be created with `is_active = False`, a verification email
will be sent including a link to verify the email and activate the account. 

###  AvatarMixin
`user_management.models.mixins.AvatarMixin` adds an avatar field. The 
serializers require `django-imagekit`.

#### Avatar views
`user_management.api.avatar.views.ProfileAvatar` provides an endpoint to retrieve 
and update the logged in user's avatar.

`user_management.api.avatar.views.UserAvatar` provides an endpoint to retrieve 
and update other user's avatar. Only admin user can update other user's data.

Both avatar views provides an endpoint to retrieve a thumbnail of the
authenticated user's avatar.

    Thumbnail options can be specified as get parameters. Options are:
        width: Specify the width (in pixels) to resize / crop to.
        height: Specify the height (in pixels) to resize / crop to.
        crop: Whether to crop or not [1,0]
        anchor: Where to anchor the crop [t,r,b,l]
        upscale: Whether to upscale or not [1,0]

    If no options are specified the users avatar is returned.

    To crop avatar to 100x100 anchored to the top right:
        avatar?width=100&height=100&crop=1&anchor=tr


## Installation
Install the package

    pip install django-user-management

Install with avatar functionality

    pip install django-user-management[avatar]


Create a custom user model

    from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
    from user_management.models.mixins import ActiveUserMixin


    class User(ActiveUserMixin, PermissionsMixin, AbstractBaseUser):
        pass

If you want to use the `VerifyEmailMixin` then substitute it for `ActiveUserMixin`


Make sure your custom user model in added to `INSTALLED_APPS` and set 
`AUTH_USER_MODEL` to your custom user model.


## Dependencies
    
    djangorestframework
    incuna_mail

The optional `AvatarMixin` functionality depends on `django-imagekit`.


### To use the api views
Add to your `INSTALLED_APPS` in `settings.py`

    INSTALLED_APPS = (
        ...
        'user_management.api',
        ...
    )

Set your `DEFAULT_AUTHENTICATION_CLASSES`, for example:

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': {
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        },
    }

Add the urls to your `ROOT_URLCONF`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.urls', namespace='user_management_api')),
        ...
    )

If you are using the `VerifyEmailMixin` then also include
`user_management.api.urls.verify_email`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.urls.verify_email')),
        ...
    )

If you are using the `AvatarMixin` then also include
`user_management.api.avatar.urls.avatar`

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.avatar.urls.avatar')),
        ...
    )


If you need more fine-grained control you can replace `user_management.api.urls`
with a selection from

    urlpatterns = patterns(''
        ...
        url('', include('user_management.api.urls.auth')),
        url('', include('user_management.api.urls.password_reset')),
        url('', include('user_management.api.urls.profile')),
        url('', include('user_management.api.urls.register')),
        ...
    )


### Throttling protection
The `/auth/` and `/auth/password_reset/` URLs are protected against throttling
using the built-in [DRF throttle module](http://www.django-rest-framework.org/api-guide/throttling).

The default throttle rates are:
    
    'logins': '10/hour'
    'passwords': '3/hour'

You can customise the throttling rates by setting `DEFAULT_THROTTLE_RATES`
in your `settings.py`:

    DEFAULT_THROTTLE_RATES = {
        'logins': '100/day',
        'passwords': 100/day',
    }
