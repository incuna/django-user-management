from django.conf.urls import url

from . import views


app_name = 'user_management_ui'
urlpatterns = [
    url(
        r'^register/verify/(?P<token>[0-9A-Za-z:\-_]+)/$',
        views.VerifyUserEmailView.as_view(),
        name='registration-verify',
    ),
]
