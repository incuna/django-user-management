from django.conf.urls import url

from .. import views


urlpatterns = [
    url(
        regex=r'^profile/avatar/?$',
        view=views.ProfileAvatar.as_view(),
        name='profile_avatar',
    ),
]
