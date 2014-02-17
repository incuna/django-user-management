from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',

    url(
        regex=r'^profile/?$',
        view=views.ProfileDetail.as_view(),
        name='profile_detail',
    ),
    url(
        regex=r'^profile/password/?$',
        view=views.PasswordChange.as_view(),
        name='password_change',
    ),
)
