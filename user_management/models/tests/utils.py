from incuna_test_utils.testcases.api_request import BaseAPIRequestTestCase
from incuna_test_utils.testcases.request import BaseRequestTestCase

from .factories import UserFactory


class APIRequestTestCase(BaseAPIRequestTestCase):
    user_factory = UserFactory


class RequestTestCase(BaseRequestTestCase):
    user_factory = UserFactory
