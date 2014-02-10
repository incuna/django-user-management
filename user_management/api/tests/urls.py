from django.conf.urls import include, patterns, url


urlpatterns = patterns('',
    url(r'', include('user_management.api.verify_email_urls')),
)
