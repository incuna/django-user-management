from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.test import override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_management.models.tests.factories import VerifyEmailUserFactory
from user_management.models.tests.models import VerifyEmailUser
from user_management.models.tests.utils import RequestTestCase
from .. import views


@override_settings(AUTH_USER_MODEL='tests.VerifyEmailUser')
class TestVerifyUserEmailView(RequestTestCase):
    view_class = views.VerifyUserEmailView

    def test_get(self):
        """A user clicks the link in their email and activates their account."""
        user = VerifyEmailUserFactory.create(email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

        user = VerifyEmailUser.objects.get(pk=user.pk)

        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)

        self.assertEqual(
            self.view_class.success_message,
            str(request._messages.store[0]),
        )

    def test_get_nonsense_uid(self):
        """The view is accessed with a broken UID and 404s."""
        user = VerifyEmailUserFactory.create(email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(424242))
        token = default_token_generator.make_token(user)

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(Http404)):
            view(request, uidb64=uid, token=token)

    def test_get_nonsense_token(self):
        """The view is accessed with a broken token and 404s."""
        user = VerifyEmailUserFactory.create(email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = 'I_am_a_token'

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(Http404)):
            view(request, uidb64=uid, token=token)

    def test_get_registered_user(self):
        """The view is accessed for an already-verified user and 403s."""
        user = VerifyEmailUserFactory.create(email_verified=True)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(PermissionDenied)):
            view(request, uidb64=uid, token=token)
