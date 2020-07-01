# Views

## To use the API views

Add to your `INSTALLED_APPS` in `settings.py`:

    INSTALLED_APPS = (
        ...
        'user_management.api',
        ...
    )

Ensure your `DEFAULT_AUTHENTICATION_CLASSES` include the following:

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': {
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        },
    }

Add the URLs to your `ROOT_URLCONF`:

    urlpatterns = [
        ...
        url('', include('user_management.api.urls', namespace='user_management_api_core')),
        ...
    ]

If you are using the `VerifyEmailMixin`, then you'll also need to include
`user_management.api.urls.verify_email` or `user_management.ui.urls`:

    urlpatterns = [
        ...
        url('', include('user_management.api.urls.verify_email', namespace='user_management_api_verify')),  # or
        url('', include('user_management.ui.urls', namespace='user_management_ui')),
        ...
    ]

If you are using the `AvatarMixin`, then you'll also need to include
`user_management.api.avatar.urls.avatar`:

    urlpatterns = [
        ...
        url('', include('user_management.api.avatar.urls.avatar', namespace='user_management_api_avatar')),
        ...
    ]


If you need more fine-grained control, you can replace `user_management.api.urls`
with a selection from:

    urlpatterns = [
        ...
        url('', include('user_management.api.urls.auth')),
        url('', include('user_management.api.urls.password_reset')),
        url('', include('user_management.api.urls.profile')),
        url('', include('user_management.api.urls.register')),
        ...
    ]


## Throttling protection

The `/auth/` and `/auth/password_reset/` URLs are protected against throttling using the
built-in [DRF throttle module](http://www.django-rest-framework.org/api-guide/throttling).

The default throttle rates are:

    'logins': '10/hour'
    'passwords': '3/hour'

You can customise the throttling rates by setting `REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']`
in your `settings.py`:

    REST_FRAMEWORK = {
        'DEFAULT_THROTTLE_RATES': {
            'logins': '100/day',
            'passwords': 100/day',
        },
    }


## Filtering sensitive data

A custom Sentry logging class is available to prevent sensitive data from being logged
by the Sentry client.

Activate it in `settings.py` by adding:

    SENTRY_CLIENT = 'user_management.utils.sentry.SensitiveDjangoClient'


## Expiry of authentication tokens

By default, DRF does not offer expiration for authentication tokens, nor any form
of validation for the expired tokens. `django-user-management` is here to help!

To use this functionality, override the authentication class for DRF in `settings.py`:

    REST_FRAMEWORK = {
        ...
        'DEFAULT_AUTHENTICATION_CLASSES': 'user_management.api.authentication.TokenAuthentication',
        ...
    }

There's a management command that can be run regularly (e.g. via cronjob) to clear expired tokens:

    python manage.py remove_expired_tokens

### Token expiry times

You can set a custom expiry time for the auth tokens by adding the below to `settings.py`:

    AUTH_TOKEN_MAX_AGE = <seconds_value> (default: 200 days)
    AUTH_TOKEN_MAX_INACTIVITY = <seconds_value> (default: 12 hours)
