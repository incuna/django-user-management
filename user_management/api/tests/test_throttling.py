from django.core.cache import cache
from mock import patch
from rest_framework import status

from user_management.api import views
from user_management.models.tests.factories import UserFactory
from user_management.models.tests.utils import APIRequestTestCase

THROTTLE_RATE_PATH = 'rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES'


class GetTokenTest(APIRequestTestCase):
    view_class = views.GetToken

    def tearDown(self):
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
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class TestPasswordResetEmail(APIRequestTestCase):
    view_class = views.PasswordResetEmail

    def tearDown(self):
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
