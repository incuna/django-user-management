from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^auth/?$',
        view=views.GetToken.as_view(),
        name='auth',
    ),
)
