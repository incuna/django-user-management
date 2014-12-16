import binascii
import datetime
import os

from django.conf import settings
from django.db import models
from django.utils import timezone


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
# Max expiry time for auth tokens
DEFAULT_AUTH_TOKEN_MAX_AGE = 200 * DAY
# Max inactivity time
DEFAULT_AUTH_TOKEN_MAX_INACTIVITY = 12 * HOUR


def update_expiry(created=None):
    now = timezone.now()

    if created is None:
        created = now

    max_age = getattr(
        settings,
        'AUTH_TOKEN_MAX_AGE',
        DEFAULT_AUTH_TOKEN_MAX_AGE,
    )
    max_age = created + datetime.timedelta(seconds=max_age)

    max_inactivity = getattr(
        settings,
        'AUTH_TOKEN_MAX_INACTIVITY',
        DEFAULT_AUTH_TOKEN_MAX_INACTIVITY,
    )
    max_inactivity = now + datetime.timedelta(seconds=max_inactivity)

    return min(max_inactivity, max_age)


class AuthToken(models.Model):
    """
    Model for auth tokens with added functionality of controlling
    expiration time of tokens.

    Similar to DRF's model but with extra `expires` field.

    It also has FK (not OneToOne relation) to user as the user can have
    many tokens (multiple devices) in order to token expiration to work.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='authtoken')
    created = models.DateTimeField(default=timezone.now, editable=False)
    expires = models.DateTimeField(default=update_expiry, editable=False)

    def __str__(self):
        return self.key

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(AuthToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def update_expiry(self, commit=True):
        """Update token's expiration datetime on every auth action."""
        self.expires = update_expiry(self.created)
        if commit:
            self.save()
