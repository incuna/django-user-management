from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from incuna_mail import send
from rest_framework import generics, response, status, views
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import exceptions, models, permissions, serializers, throttling


User = get_user_model()


class GetAuthToken(ObtainAuthToken):
    model = models.AuthToken
    throttle_classes = [
        throttling.UsernameLoginRateThrottle,
        throttling.LoginRateThrottle,
    ]
    throttle_scope = 'logins'

    def post(self, request):
        """Create auth token. Differs from DRF that it always creates new token
        but not re-using them."""
        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token = self.model.objects.create(user=serializer.object['user'])
            token.update_expiry()
            return response.Response({'token': token.key})

        return response.Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """Delete auth token when `delete` request was issued."""
        # Logic repeated from DRF because one cannot easily reuse it
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            return response.Response(msg, status=status.HTTP_400_BAD_REQUEST)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            return response.Response(msg, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = self.model.objects.get(key=auth[1])
        except self.model.DoesNotExist:
            pass
        else:
            token.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class UserRegister(generics.CreateAPIView):
    serializer_class = serializers.RegistrationSerializer
    permission_classes = [permissions.IsNotAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.DATA,
            files=request.FILES,
        )
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
            user = User.objects.get_by_natural_key(email)
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
            raise exceptions.InvalidExpiredToken()

        token = kwargs['token']
        if not default_token_generator.check_token(self.user, token):
            raise exceptions.InvalidExpiredToken()

        return super(OneTimeUseAPIMixin, self).initial(
            request,
            *args,
            **kwargs
        )


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


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
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


class ResendConfirmationEmail(generics.GenericAPIView):
    """Resend a confirmation email."""
    permission_classes = [permissions.IsNotAuthenticated]
    serializer_class = serializers.ResendConfirmationEmailSerializer
    throttle_classes = [throttling.ResendConfirmationEmailRateThrottle]
    throttle_scope = 'confirmations'

    def post(self, request, *args, **kwargs):
        """Validate `email` and send a request to confirm it."""
        serializer = self.serializer_class(data=request.DATA)

        if not serializer.is_valid():
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.user.send_validation_email()
        msg = _('Email confirmation sent.')
        return response.Response(msg, status=status.HTTP_204_NO_CONTENT)
