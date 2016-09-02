from django.conf.urls import include, url


urlpatterns = [
    url(r'', include('user_management.api.urls.auth')),
    url(r'', include('user_management.api.urls.password_reset')),
    url(r'', include('user_management.api.urls.profile')),
    url(r'', include('user_management.api.urls.register')),
]
