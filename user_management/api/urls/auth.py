from django.conf.urls import url

from .. import views


urlpatterns = [
    url(
        regex=r'^auth/?$',
        view=views.GetAuthToken.as_view(),
        name='auth',
    ),
]
