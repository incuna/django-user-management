from django.conf.urls import include, url


urlpatterns = [
    url(r'', include('user_management.api.avatar.urls.profile_avatar')),
    url(r'', include('user_management.api.avatar.urls.user_avatar')),
]
