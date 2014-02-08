from django.conf.urls import include, patterns, url


urlpatterns = patterns('',
    url(r'', include('verified_user_management.urls')),
)

