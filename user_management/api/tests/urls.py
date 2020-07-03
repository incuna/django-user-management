from django.conf.urls import include, url
from django.contrib.auth.views import LoginView


urlpatterns = [
    url(r'', include(
        'user_management.api.urls',
        namespace='user_management_api_core',
    )),
    url(r'', include(
        'user_management.api.urls.verify_email',
        namespace='user_management_api_verify',
    )),
    url(r'', include(
        'user_management.api.urls.users',
        namespace='user_management_api_users',
    )),
    url(r'', include(
        'user_management.api.avatar.urls',
        namespace='user_management_api_avatar',
    )),
    url(r'', include(
        'user_management.ui.urls',
        namespace='user_management_ui',
    )),
    url(r'^login/$', LoginView.as_view(), name='login')
]
