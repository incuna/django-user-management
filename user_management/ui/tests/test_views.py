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

        self.assertEqual(response.url, '/accounts/login/')

        user = VerifyEmailUser.objects.get(pk=user.pk)

        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)

        self.assertEqual(
            self.view_class.success_message,
            str(request._messages.store[0]),
        )

    @override_settings(LOGIN_ON_EMAIL_VERIFICATION=True)
    def test_auto_login_get(self):
        """A user is automatically logged in when they activate their account."""
        user = VerifyEmailUserFactory.create(email_verified=False)
        token = user.generate_validation_token()

        request = self.create_request('get', auth=False)
        self.add_session_to_request(request)

        view = self.view_class.as_view()
        view(request, token=token)

        self.assertEqual(int(request.session['_auth_user_id']), user.pk)

    @override_settings(LOGIN_URL='login')
    def test_get_named_login_url(self):
        """A user clicks the link in their email and activates their account."""
        user = VerifyEmailUserFactory.create(email_verified=False)
        token = user.generate_validation_token()

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        response = view(request, token=token)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, '/login/')

    def test_get_nonsense_token(self):
        """The view is accessed with a broken token and 404s."""
        token = 'I_am_a_token'

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()
        with(self.assertRaises(self.view_class.invalid_exception_class)):
            view(request, token=token)

    def test_get_registered_user(self):
        """The view is accessed for an already-verified user then redirect."""
        user = VerifyEmailUserFactory.create(email_verified=True)
        token = user.generate_validation_token()

        request = self.create_request('get', auth=False)
        view = self.view_class.as_view()

        response = view(request, token=token)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(response.url, '/accounts/login/')

        user = VerifyEmailUser.objects.get(pk=user.pk)

        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)

        self.assertEqual(
            self.view_class.already_verified_message,
            str(request._messages.store[0]),
        )

    query_string = 'validated'

    @override_settings(VERIFIED_QUERYSTRING=query_string)
    def test_get_redirect_url_with_query_string(self):
        view = views.VerifyUserEmailView()
        view.already_verified = False
        response = view.get_redirect_url()
        expected_url = '/accounts/login/?' + self.query_string

        self.assertEqual(response, expected_url)

    @override_settings(LOGIN_URL='login')
    @override_settings(VERIFIED_QUERYSTRING=query_string)
    def test_get_redirect_url_with_query_string_and_login_url(self):
        view = views.VerifyUserEmailView()
        view.already_verified = False
        response = view.get_redirect_url()
        expected_url = '/login/?' + self.query_string

        self.assertEqual(response, expected_url)

    @override_settings(VERIFIED_QUERYSTRING=query_string)
    def test_get_redirect_url_with_verified_user(self):
        view = views.VerifyUserEmailView()
        view.already_verified = True
        response = view.get_redirect_url()

        self.assertEqual(response, '/accounts/login/')

    def test_get_redirect_url_without_query_setting(self):
        view = views.VerifyUserEmailView()
        view.already_verified = False
        response = view.get_redirect_url()

        self.assertEqual(response, '/accounts/login/')
