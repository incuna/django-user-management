from django.core.cache import cache
from django.urls import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory

from user_management.api import views
from user_management.models.tests.factories import UserFactory
from user_management.models.tests.utils import APIRequestTestCase
from .. import throttling

THROTTLE_RATE_PATH = 'rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES'


class ClearCacheMixin:
    """Clear cache on `tearDown`.

    `django-rest-framework` puts a successful (not throttled) request into a cache."""
    def tearDown(self):
        cache.clear()


class GetAuthTokenTest(ClearCacheMixin, APIRequestTestCase):
    """Test `GetAuthToken` is throttled."""
    throttle_expected_status = status.HTTP_429_TOO_MANY_REQUESTS
    view_class = views.GetAuthToken

    def setUp(self):
        self.auth_url = reverse('user_management_api_core:auth')

    @patch(THROTTLE_RATE_PATH, new={'logins': '1/minute'})
    def test_user_auth_throttle(self):
        """Ensure POST requests are throttled correctly."""
        data = {
            'username': 'jimmy@example.com',
            'password': 'password;lol',
        }
        view = self.view_class.as_view()

        # no token attached hence HTTP 400
        request = self.create_request('post', auth=False, data=data)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # request should be throttled now
        # (new request created to prevent django.http.request.RawPostDataException)
        request = self.create_request('post', auth=False, data=data)
        response = view(request)
        self.assertEqual(response.status_code, self.throttle_expected_status)

    @patch(THROTTLE_RATE_PATH, new={'logins': '1/minute'})
    def test_user_auth_throttle_ip(self):
        """Ensure user gets throttled from a single IP address."""
        data = {}

        request = APIRequestFactory().post(self.auth_url, data, REMOTE_ADDR='127.0.0.1')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        request = APIRequestFactory().post(self.auth_url, data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, self.throttle_expected_status)

    @patch(THROTTLE_RATE_PATH, new={'logins': '1/minute'})
    def test_user_auth_throttle_username(self):
        """Ensure username is throttled no matter what IP the user connects on."""
        data = {'username': 'jimmy'}
        request = APIRequestFactory().post(self.auth_url, data, REMOTE_ADDR='127.0.0.1')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Different user name to different ip is not throttled
        data2 = {'username': 'another_jimmy_here'}
        request = APIRequestFactory().post(self.auth_url, data2, REMOTE_ADDR='127.0.0.2')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Same username to different ip is throttled
        request = APIRequestFactory().post(self.auth_url, data, REMOTE_ADDR='127.0.0.3')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, self.throttle_expected_status)

    @patch(THROTTLE_RATE_PATH, new={'logins': '1/minute'})
    def test_authenticated_user_not_throttled(self):
        """An authenticated user is not throttled by UsernameLoginRateThrottle."""

        class View(self.view_class):
            throttle_classes = [throttling.UsernameLoginRateThrottle]

        view = View.as_view()

        # We are not throttled here
        request = self.create_request('post', data={})
        response = view(request)
        self.assertNotEqual(response.status_code, self.throttle_expected_status)

        # Or here
        # (new request created to prevent django.http.request.RawPostDataException)
        request = self.create_request('post', data={})
        response = view(request)
        self.assertNotEqual(response.status_code, self.throttle_expected_status)


class TestPasswordResetEmail(ClearCacheMixin, APIRequestTestCase):
    """Test `PasswordResetEmail` is throttled."""
    view_class = views.PasswordResetEmail

    @patch(THROTTLE_RATE_PATH, new={'passwords': '1/minute'})
    def test_post_rate_limit(self):
        """Ensure the POST requests are rate limited."""
        email = 'exists@example.com'
        UserFactory.create(email=email)

        data = {'email': email}
        request = self.create_request('post', data=data, auth=False)
        view = self.view_class.as_view()

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # request is throttled
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class TestResendConfirmationEmail(ClearCacheMixin, APIRequestTestCase):
    """Test `ResendConfirmationEmail` is throttled."""
    view_class = views.ResendConfirmationEmail

    @patch(THROTTLE_RATE_PATH, new={'confirmations': '1/minute'})
    def test_post_rate_limit(self):
        """Assert POST requests are rate limited."""
        user = UserFactory.create()
        data = {'email': user.email}

        request = self.create_request('post', data=data, auth=False)
        view = self.view_class.as_view()

        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Duplicate the request here as we are accessing request.data twice. To
        # get the `request.data`, `djangorestframework` `read` the `POST` request
        # (a stream) without rewinding the stream.
        # This was producing an `Assertion` error only happening in test where
        # calling the `view` with the same `request` twice is returning:
        # {'detail': 'JSON parse error - No JSON object could be decoded'}`
        # https://github.com/tomchristie/django-rest-framework/blob/650a91ac24cbd3e5b4ad5d7d7c6706fdf6160a78/rest_framework/parsers.py#L60-L64
        request = self.create_request('post', data=data, auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
            msg=response.data,
        )
