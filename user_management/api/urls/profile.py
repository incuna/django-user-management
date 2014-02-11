from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^profile$',
        view=views.ProfileListView.as_view(),
        name='profile_list',
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
