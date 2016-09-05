from django.conf.urls import url

from .. import views


urlpatterns = [
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
]
