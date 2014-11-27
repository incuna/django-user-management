from django.core.cache import cache
from django.core.urlresolvers import reverse
from mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory

from user_management.api import views
from user_management.models.tests.factories import UserFactory
from user_management.models.tests.utils import APIRequestTestCase

THROTTLE_RATE_PATH = 'rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES'


class GetAuthTokenTest(APIRequestTestCase):
    throttle_expected_status = status.HTTP_429_TOO_MANY_REQUESTS
    view_class = views.GetAuthToken

    def setUp(self):
        self.auth_url = reverse('user_management_api:auth')

    def tearDown(self):
        # DRF puts a successful (not throttled) request onto a cache
        cache.clear()

    @patch(THROTTLE_RATE_PATH, new={'logins': '1/minute'})
    def test_user_auth_throttle(self):
        """Ensure POST requests are throttled correctly."""
        data = {
            'username': 'jimmy@example.com',
            'password': 'password;lol',
        }
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()

        # no token attached hence HTTP 400
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # request should be throttled now
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


class TestPasswordResetEmail(APIRequestTestCase):
    view_class = views.PasswordResetEmail

    def tearDown(self):
        # DRF puts a successful (not throttled) request onto a cache
        cache.clear()

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
