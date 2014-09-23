from incuna_test_utils.compat import Python2AssertMixin
from incuna_test_utils.testcases.api_request import BaseAPIRequestTestCase
from incuna_test_utils.testcases.request import BaseRequestTestCase

from .factories import UserFactory


class APIRequestTestCase(Python2AssertMixin, BaseAPIRequestTestCase):
    user_factory = UserFactory


class RequestTestCase(Python2AssertMixin, BaseRequestTestCase):
    user_factory = UserFactory
