from incuna_test_utils.compat import wipe_id_fields_on_django_lt_17

from user_management.models.tests import factories, utils
from ..models import AuthToken


class TestAuthToken(utils.APIRequestTestCase):
    model = AuthToken

    def test_fields(self):
        fields = self.model._meta.get_all_field_names()

        expected = wipe_id_fields_on_django_lt_17((
            # Inherited from subclassed model
            'key',
            'user',
            'user_id',
            'created',

            'expires',
        ))

        self.assertCountEqual(fields, expected)

    def test_unicode(self):
        uni_key = 'OSSUM'
        obj = self.model(key=uni_key)
        self.assertEqual(str(obj), uni_key)

    def test_multiple_tokens(self):
        user = factories.UserFactory.create()
        tokens = factories.AuthTokenFactory.create_batch(2, user=user)

        expected_tokens = self.model.objects.filter(user=user)

        self.assertCountEqual(tokens, expected_tokens)
