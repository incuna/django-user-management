from django.test import TestCase

from ..models import AuthToken
from user_management.models.tests.factories import AuthTokenFactory, UserFactory


class TestAuthToken(TestCase):
    model = AuthToken

    def test_fields(self):
        fields = self.model._meta.get_all_field_names()

        expected = {
            # Inherited from subclassed model
            'key',
            'user',
            'user_id',
            'created',

            'expires',
        }

        try:
            # python 3 only:
            self.assertCountEqual(fields, expected)
        except AttributeError:
            # python 2 only:
            self.assertItemsEqual(fields, expected)

    def test_unicode(self):
        uni_key = 'OSSUM'
        obj = self.model(key=uni_key)
        self.assertEqual(str(obj), uni_key)

    def test_multiple_tokens(self):
        user = UserFactory.create()
        tokens = AuthTokenFactory.create_batch(2, user=user)

        expected_tokens = self.model.objects.filter(user=user)

        try:
            # python 3 only:
            self.assertCountEqual(tokens, expected_tokens)
        except AttributeError:
            # python 2 only:
            self.assertItemsEqual(tokens, expected_tokens)
