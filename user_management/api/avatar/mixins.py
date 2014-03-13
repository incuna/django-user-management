from django.db import models


class AvatarMixin(models.Model):
    avatar = models.ImageField(upload_to='user_avatar', null=True, blank=True)

    class Meta:
        abstract = True
