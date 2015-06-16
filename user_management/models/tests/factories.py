import factory

from django.contrib.auth import get_user_model

from user_management.api.models import AuthToken


class UserFactory(factory.DjangoModelFactory):
    name = factory.Sequence('Test User {}'.format)
    email = factory.Sequence('email{}@example.com'.format)
    is_active = True

    class Meta:
        model = get_user_model()

    @factory.post_generation
    def password(self, create, extracted='default password', **kwargs):
        self.raw_password = extracted
        self.set_password(self.raw_password)
        if create:
            self.save()


class AuthTokenFactory(factory.DjangoModelFactory):
    key = factory.Sequence('key{}'.format)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = AuthToken
