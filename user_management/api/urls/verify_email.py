from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=(
            r'^verify_email/(?P<token>[0-9A-Za-z:\-_]+)/?$'
        ),
        view=csrf_exempt(views.VerifyAccountView.as_view()),
        name='verify_user',
    ),
)
