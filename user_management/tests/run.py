#! /usr/bin/env python
"""From http://stackoverflow.com/a/12260597/400691"""
import os
import sys
from ast import literal_eval

import dj_database_url
import django
from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings


KEEPDB = literal_eval(os.environ.get('KEEPDB', 'False'))
MIGRATION_MODULES = {
    'api': 'user_management.tests.testmigrations.api',
    'tests': 'user_management.tests.testmigrations.tests',
}


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
        'django.contrib.messages',

        'rest_framework.authtoken',

        # Added for templates
        'user_management.api',
        'user_management.ui',
        'user_management.models.tests',
    ),
    PASSWORD_HASHERS=('django.contrib.auth.hashers.MD5PasswordHasher',),
    SITE_ID=1,
    AUTH_USER_MODEL='tests.User',
    AUTHENTICATION_BACKENDS=(
        'user_management.models.backends.CaseInsensitiveEmailBackend',
    ),
    MIDDLEWARE=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ),
    ROOT_URLCONF='user_management.api.tests.urls',
    REST_FRAMEWORK={
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
        ),
    },
    SENTRY_CLIENT='user_management.utils.sentry.SensitiveDjangoClient',
    USE_TZ=True,
    TIME_ZONE='UTC',
    MIGRATION_MODULES=MIGRATION_MODULES,
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ]
            }
        },
    ]
)


django.setup()


# DiscoverRunner requires `django.setup()` to have been called
from django.test.runner import DiscoverRunner  # noqa


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    pass


test_runner = TestRunner(verbosity=1, keepdb=KEEPDB)
failures = test_runner.run_tests(['user_management'])
if failures:
    sys.exit(1)
