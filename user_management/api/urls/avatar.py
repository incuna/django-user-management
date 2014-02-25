from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^avatar/?$',
        view=views.Avatar.as_view(),
        name='avatar',
    ),
    url(
        regex=r'^avatar-thumbnail/?$',
        view=views.AvatarThumbnail.as_view(),
        name='avatar-thumbnail',
    ),
)
