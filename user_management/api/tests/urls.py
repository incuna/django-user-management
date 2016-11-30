from django.conf.urls import include, url
from django.contrib.auth.views import login


urlpatterns = [
    url(r'', include(
        [
            url(r'', include('user_management.api.urls')),
            url(r'', include('user_management.api.urls.verify_email')),
            url(r'', include('user_management.api.urls.users')),
            url(r'', include('user_management.api.avatar.urls')),
            url(r'', include('user_management.ui.urls')),
        ],
        namespace='user_management_api'
    )),
    url(r'^login/$', login, name='login')
]
