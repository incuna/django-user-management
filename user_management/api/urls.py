from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from . import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^auth/?$',
        view=views.GetToken.as_view(),
        name='auth',
    ),
    url(
        regex=r'^auth/password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=csrf_exempt(views.PasswordResetView.as_view()),
        name='password_reset_confirm',
    ),
    url(
        regex=r'^auth/password_reset/$',
        view=views.PasswordResetEmailView.as_view(),
        name='password_reset',
    ),
    url(
        regex=r'^profile/$',
        view=views.ProfileDetailView.as_view(),
        name='profile_detail',
    ),
    url(
        regex=r'^profile/password/$',
        view=views.PasswordChangeView.as_view(),
        name='password_change',
    ),
)
