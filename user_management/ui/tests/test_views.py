from django.test import override_settings

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
        token = user.generate_validation_token()

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        response = view(request, token=token)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/accounts/login/?next=/')

        user = VerifyEmailUser.objects.get(pk=user.pk)

        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)

        self.assertEqual(
            self.view_class.success_message,
            str(request._messages.store[0]),
        )

    def test_get_nonsense_token(self):
        """The view is accessed with a broken token and 404s."""
        token = 'I_am_a_token'

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(self.view_class.invalid_exception_class)):
            view(request, token=token)

    def test_get_registered_user(self):
        """The view is accessed for an already-verified user and 403s."""
        user = VerifyEmailUserFactory.create(email_verified=True)
        token = user.generate_validation_token()

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(self.view_class.permission_denied_class)):
            view(request, token=token)
