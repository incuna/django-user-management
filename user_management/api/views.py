from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.http import Http404
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send
from rest_framework import generics, renderers, response, status, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import permissions, serializers, throttling


User = get_user_model()


class GetToken(ObtainAuthToken):
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer)
    throttle_classes = [throttling.LoginRateThrottle]
    throttle_scope = 'logins'

    def delete(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            pass
        else:
            token.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserRegister(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer
    permission_classes = [permissions.IsNotAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)
        if serializer.is_valid():
            return self.is_valid(serializer)
        return self.is_invalid(serializer)

    def is_invalid(self, serializer):
        return response.Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def is_valid(self, serializer):
        serializer.save()
        if serializer.object.email_verification_required:
            serializer.object.send_validation_email()
            ok_message = _(
                'Your account has been created and an activation link sent ' +
                'to your email address. Please check your email to continue.'
            )
        else:
            ok_message = _('Your account has been created.')

        return response.Response(
            data={'data': ok_message},
            status=status.HTTP_201_CREATED,
        )


class PasswordResetEmail(generics.GenericAPIView):
    permission_classes = [permissions.IsNotAuthenticated]
    template_name = 'user_management/password_reset_email.html'
    serializer_class = serializers.PasswordResetEmailSerializer
    throttle_classes = [throttling.PasswordResetRateThrottle]
    throttle_scope = 'passwords'

    def email_context(self, site, user):
        return {
            'protocol': 'https',
            'site': site,
            'token': default_token_generator.make_token(user),
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.DATA)
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

        msg = _('Password reset request successful. Please check your email.')
        return response.Response(msg, status=status.HTTP_204_NO_CONTENT)

    def send_email(self, user):
        site = Site.objects.get_current()
        send(
            to=[user.email],
            template_name=self.template_name,
            subject=_('{domain} password reset').format(domain=site.domain),
            context=self.email_context(site, user),
        )


class OneTimeUseAPIMixin(object):
    def initial(self, request, *args, **kwargs):
        uidb64 = kwargs['uidb64']
        uid = urlsafe_base64_decode(force_text(uidb64))

        try:
            self.user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            raise Http404()

        token = kwargs['token']
        if not default_token_generator.check_token(self.user, token):
            raise Http404()

        return super(OneTimeUseAPIMixin, self).initial(request, *args, **kwargs)


class PasswordReset(OneTimeUseAPIMixin, generics.UpdateAPIView):
    permission_classes = [permissions.IsNotAuthenticated]
    model = User
    serializer_class = serializers.PasswordResetSerializer

    def get_object(self):
        return self.user


class PasswordChange(generics.UpdateAPIView):
    model = User
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.PasswordChangeSerializer

    def get_object(self):
        return self.request.user


class VerifyAccountView(OneTimeUseAPIMixin, views.APIView):
    permission_classes = [AllowAny]
    ok_message = _('Your account has been verified.')

    def post(self, request, *args, **kwargs):
        if not self.user.email_verification_required:
            return response.Response(status=status.HTTP_403_FORBIDDEN)

        self.user.email_verification_required = False
        self.user.is_active = True
        self.user.save()

        return response.Response(
            data={'data': self.ok_message},
            status=status.HTTP_201_CREATED,
        )


class ProfileDetail(generics.RetrieveUpdateAPIView):
    model = User
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user


class UserList(generics.ListCreateAPIView):
    model = User
    permission_classes = (IsAuthenticated, permissions.IsAdminOrReadOnly)
    serializer_class = serializers.UserSerializerCreate


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    model = User
    permission_classes = (IsAuthenticated, permissions.IsAdminOrReadOnly)
    serializer_class = serializers.UserSerializer
