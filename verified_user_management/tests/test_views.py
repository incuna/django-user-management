from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_management.tests.utils import APIRequestTestCase
from user_management.tests.factories import UserFactory

from .. import views


User = get_user_model()


class TestVerifyAccountView(APIRequestTestCase):
    view_class = views.VerifyAccountView

    def test_post_authenticated(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post', auth=True)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 200)

        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.verified_email)
        self.assertTrue(updated_user.is_active)

    def test_post_unauthenticated(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 200)

        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.verified_email)
        self.assertTrue(updated_user.is_active)

    def test_post_invalid_user(self):
        # There should never be a user with pk 0
        invalid_uid = urlsafe_base64_encode(b'0')

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=invalid_uid)
        self.assertEqual(response.status_code, 404)

    def test_post_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 404)

    def test_post_verified_email(self):
        user = UserFactory.create(verified_email=True)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 403)

    def test_post_different_user_logged_in(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post', user=other_user)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 200)

        updated_user = User.objects.get(pk=user.pk)
        self.assertTrue(updated_user.verified_email)

        logged_in_user = User.objects.get(pk=other_user.pk)
        self.assertFalse(logged_in_user.verified_email)
