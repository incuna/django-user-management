from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from user_management.urls import urlpatterns
from . import views


urlpatterns += patterns(
    url(
        regex=r'^verify_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        view=csrf_exempt(views.VerifyAccountView.as_view()),
        name='verify_user',
    ),
)
