from django.conf.urls import include, patterns, url


urlpatterns = patterns(
    '',
    url(r'', include('user_management.api.avatar.urls.profile_avatar')),
    url(r'', include('user_management.api.avatar.urls.user_avatar')),
)
