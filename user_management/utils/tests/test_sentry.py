from raven.contrib.django.models import get_client
from rest_framework.test import APIRequestFactory

from user_management.models.tests.utils import APIRequestTestCase


class TestSentryClient(APIRequestTestCase):
    def test_cookies(self):
        request = APIRequestFactory().post('/')
        request.COOKIES['username'] = 'jimmy'

        raven = get_client()
        result = raven.get_data_from_request(request)

        self.assertFalse('cookies' in result['request'])
        self.assertFalse('Cookie' in result['request']['headers'])
