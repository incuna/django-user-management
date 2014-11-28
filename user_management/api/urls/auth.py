from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^auth/?$',
        view=views.GetAuthToken.as_view(),
        name='auth',
    ),
)
