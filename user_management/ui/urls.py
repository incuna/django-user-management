from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^register/verify/(?P<uidb64>[a-zA-Z0-9_-]+)/(?P<token>[a-zA-Z0-9_-]+)/$',
        views.VerifyUserEmailView.as_view(),
        name='registration-verify',
    ),
]
