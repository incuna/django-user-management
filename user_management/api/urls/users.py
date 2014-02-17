from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^users/?$',
        view=views.UserList.as_view(),
        name='user_list'
    ),
    url(
        regex=r'^users/(?P<pk>\d+)/?$',
        view=views.UserDetail.as_view(),
        name='user_detail'
    ),
)
