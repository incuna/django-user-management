from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send
from rest_framework import generics, renderers, response, status, views
from rest_framework.authtoken.views import ObtainAuthToken

from . import serializers, permissions


User = get_user_model()


class GetToken(ObtainAuthToken):
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer)


class UserRegister(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer
    permission_classes = [permissions.IsNotAuthenticated]
    ok_message = _('Your account has been created and an activation link sent to your email address. Please check your email to continue.')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if not serializer.is_valid():
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return response.Response(
            data={'data': self.ok_message},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetEmailView(views.APIView):
    permission_classes = [permissions.IsNotAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetEmailSerializer(data=request.DATA)
        if not serializer.is_valid():
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.data['email']
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            pass
        else:
            self.send_email(user)

        msg = 'Password reset request successful. Please check your email.'
        return response.Response(msg, status=status.HTTP_204_NO_CONTENT)

    def send_email(self, user):
        site = Site.objects.get_current()
        context = {
            'protocol': 'https',
            'token': default_token_generator.make_token(user),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        }
        send(
            to=[user.email],
            template_name='user_management/password_reset_email.html',
            subject='{} password reset'.format(site.domain),
            extra_context=context,
        )


class OneTimeUseAPIMixin:
    def dispatch(self, request, *args, **kwargs):
        uidb64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(force_text(uidb64))

        try:
            self.user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        token = kwargs['token']
        if not default_token_generator.check_token(self.user, token):
            return response.Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class PasswordResetView(OneTimeUseAPIMixin, generics.UpdateAPIView):
    permission_classes = [permissions.IsNotAuthenticated]
    model = User
    serializer_class = serializers.PasswordResetSerializer

    def get_object(self):
        return self.user


class PasswordChangeView(generics.UpdateAPIView):
    model = User
    serializer_class = serializers.PasswordChangeSerializer

    def get_object(self):
        return self.request.user


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    model = User
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user
