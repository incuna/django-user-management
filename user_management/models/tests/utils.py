from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from .factories import UserFactory


class APIRequestTestCase(TestCase):
    user_factory = UserFactory

    def create_request(self, method='get', url='/', user=None, auth=True, **kwargs):
        if not user:
            if auth:
                user = self.user_factory.create()
            else:
                user = AnonymousUser()
        kwargs['format'] = 'json'
        request = getattr(APIRequestFactory(), method)(url, **kwargs)
        request.user = user
        if auth:
            force_authenticate(request, user)
        if 'data' in kwargs:
            request.DATA = kwargs['data']
        return request
