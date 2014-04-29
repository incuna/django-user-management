import factory

from django.contrib.auth import get_user_model


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = get_user_model()
    name = factory.Sequence(lambda i: 'Test User {}'.format(i))
    email = factory.Sequence(lambda i: 'email{}@example.com'.format(i))

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create=False, **kwargs)
        user.set_password(password)
        user.raw_password = password
        if create:
            user.save()
        return user
