# Views

## To use the api views
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


## Throttling protection
The `/auth/` and `/auth/password_reset/` URLs are protected against throttling
using the built-in [DRF throttle module](http://www.django-rest-framework.org/api-guide/throttling).

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

Custom Sentry logging class is available to disallow sensitive data being logged
by Sentry client.

Activate it in the `settings.py` by adding:

    SENTRY_CLIENT = 'user_management.utils.sentry.SensitiveDjangoClient'


## Expiry of Auth tokens

By default DRF does not offer expiration for authorization tokens nor any form
of validation for the expired tokens.

`django-user-management` comes in help here and this functionality can be
easily activated.

Override the authentication class for DRF in `settings.py`:

    REST_FRAMEWORK = {
        ...
        'DEFAULT_AUTHENTICATION_CLASSES': 'user_management.api.authentication.TokenAuthentication',
        ...
    }

Remember to run the management command (eg via cronjob) to clear expired tokens:

    python manage.py remove_expired_tokens

### Tokens expiry times

You can set custom expiry time for the auth tokens.

Add below constants in the `settings.py`:

    AUTH_TOKEN_MAX_AGE = <milliseconds_value> (default: 200 days)
    AUTH_TOKEN_MAX_INACTIVITY = <milliseconds_value> (default: 12 hours)
