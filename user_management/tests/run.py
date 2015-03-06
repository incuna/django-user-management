#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691"""
import sys

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings


settings.configure(
    DATABASES={
        'default': dj_database_url.config(
            default='postgres://localhost/user_management_api',
        ),
    },
    DEFAULT_FILE_STORAGE='inmemorystorage.InMemoryStorage',
    INSTALLED_APPS=(
        # Put contenttypes before auth to work around test issue.
        # See: https://code.djangoproject.com/ticket/10827#comment:12
        'django.contrib.sites',
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.admin',

        'rest_framework.authtoken',

        # Added for templates
        'user_management.api',
        'user_management.models.tests',
    ),
    PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),
    SITE_ID=1,
    AUTH_USER_MODEL='tests.User',
    AUTHENTICATION_BACKENDS=(
        'user_management.models.backends.CaseInsensitiveEmailBackend',
    ),
    MIDDLEWARE_CLASSES=(),
    ROOT_URLCONF='user_management.api.tests.urls',
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
        ),
    },
    SENTRY_CLIENT='user_management.utils.sentry.SensitiveDjangoClient',
    USE_TZ=True,
)


if django.VERSION >= (1, 7):
    django.setup()


# DiscoverRunner requires `django.setup()` to have been called
from django.test.runner import DiscoverRunner  # noqa


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    pass


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['user_management'])
if failures:
    sys.exit(1)
