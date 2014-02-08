from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send
from user_management.models import AbstractUser


class AbstractVerifiedUser(AbstractUser):
    verified_email = models.BooleanField(_('Verified email address'), default=False)

    def save(self, *args, **kwargs):
        super(AbstractVerifiedUser, self).save(*args, **kwargs)
        if not self.verified_email:
            self.send_validation_email()

    def send_validation_email(self):
        if self.verified_email:
            raise ValueError('Cannot validate already active user.')

        context = {
            'uid': urlsafe_base64_encode(force_bytes(self.pk)),
            'token': default_token_generator.make_token(self),
        }
        site = Site.objects.get_current()

        send(
            to=[self.email],
            template_name='user_management/account_validation_email.html',
            subject='{} account validate'.format(site.domain),
            extra_context=context,
        )
