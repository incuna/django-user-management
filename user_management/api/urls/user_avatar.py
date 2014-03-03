from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^users/(?P<pk>\d+)/avatar/?$',
        view=views.UserAvatar.as_view(),
        name='user_avatar',
    ),
)
