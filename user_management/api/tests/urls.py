from django.conf.urls import include, url


urlpatterns = [
    url(r'', include(
        [
            url(r'', include('user_management.api.urls')),
            url(r'', include('user_management.api.urls.verify_email')),
            url(r'', include('user_management.api.urls.users')),
            url(r'', include('user_management.api.avatar.urls')),
        ],
        namespace='user_management_api'
    ))
]
