from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .. import views


urlpatterns = [
    url(
        regex=(
            r'^verify_email/(?P<token>[0-9A-Za-z:\-_]+)/?$'
        ),
        view=csrf_exempt(views.VerifyAccountView.as_view()),
        name='verify_user',
    ),
]
