from django.conf.urls import url

from .. import views


urlpatterns = [
    url(
        regex=r'^users/(?P<pk>\d+)/avatar/?$',
        view=views.UserAvatar.as_view(),
        name='user_avatar',
    ),
]
