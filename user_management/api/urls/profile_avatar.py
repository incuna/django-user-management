from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^profile/avatar/?$',
        view=views.ProfileAvatar.as_view(),
        name='profile_avatar',
    ),
)
