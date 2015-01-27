from django.conf.urls import patterns, url

from .. import views


urlpatterns = patterns(
    '',
    url(
        regex=r'^register/?$',
        view=views.UserRegister.as_view(),
        name='register',
    ),
    url(
        regex=r'^resend-confirmation-email/?$',
        view=views.ResendConfirmationEmail.as_view(),
        name='resend_confirmation_email',
    ),
)
