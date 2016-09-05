from django.conf.urls import url

from .. import views


urlpatterns = [
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
]
