SECRET_KEY = 'not-for-production'
DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = (
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
)

AUTH_USER_MODEL = 'tests.User'

MIDDLEWARE_CLASSES = ()

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MIGRATION_MODULES = {
    'api': 'user_management.tests.testmigrations.api',
    'tests': 'user_management.tests.testmigrations.tests',
}
