from mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from user_management.api import views
from user_management.models.tests.factories import UserFactory
from user_management.models.tests.utils import APIRequestTestCase


User = get_user_model()


class TestRegisterView(APIRequestTestCase):
    view_class = views.UserRegister

    def setUp(self):
        super(TestRegisterView, self).setUp()
        self.data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': 'bobby.tables+327@xkcd.com',
            'password': 'Sup3RSecre7paSSw0rD',
            'password2': 'Sup3RSecre7paSSw0rD',
        }

    def test_authenticated_user_post(self):
        """Authenticated Users should not be able to re-register."""
        request = self.create_request('post', auth=True, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_post(self):
        """Unauthenticated Users should be able to register."""
        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, 201)

        user = User.objects.get()
        self.assertEqual(user.name, self.data['name'])
        self.assertEqual(user.email, self.data['email'])
        # Should be hash, not literal password
        self.assertNotEqual(user.password, self.data['password'])

        # Password should validate
        self.assertTrue(check_password(self.data['password'], user.password))

    def test_post_with_missing_data(self):
        """Password should not be sent back on failed request."""
        self.data.pop('name')
        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, 400)

        self.assertTrue('name' in response.data)
        self.assertFalse('password' in response.data)
        self.assertFalse(User.objects.count())

    def test_post_password_mismatch(self):
        """Password and password2 should be the same."""
        self.data['password2'] = 'something_different'
        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertIn('password2', response.data)

        self.assertFalse(User.objects.count())

    def test_duplicate_email(self):
        """Emails should be unique regardless of case."""
        # First create a user with the same email.
        self.data.pop('password2')
        UserFactory.create(**self.data)

        # Just for kicks, lets try changing the email case.
        self.data['email'] = self.data['email'].upper()

        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, 400)

        self.assertTrue('email' in response.data)

        self.assertFalse(User.objects.count() > 1)


class TestPasswordResetEmailView(APIRequestTestCase):
    view_class = views.PasswordResetEmailView

    def test_existent_email(self):
        email = 'exists@example.com'
        user = UserFactory.create(email=email)

        request = self.create_request('post', data={'email': email}, auth=False)
        view = self.view_class.as_view()
        with patch.object(self.view_class, 'send_email') as send_email:
            response = view(request)
        self.assertEqual(response.status_code, 204)

        send_email.assert_called_once_with(user)

    def test_authenticated(self):
        request = self.create_request('post', auth=True)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_non_existent_email(self):
        email = 'doesnotexist@example.com'
        UserFactory.create(email='exists@example.com')

        request = self.create_request('post', data={'email': email}, auth=False)
        view = self.view_class.as_view()
        with patch.object(self.view_class, 'send_email') as send_email:
            response = view(request)
        self.assertEqual(response.status_code, 204)

        self.assertFalse(send_email.called)

    def test_missing_email(self):
        request = self.create_request('post', auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_send_email(self):
        email = 'test@example.com'
        user = UserFactory.create(
            email=email,
            # Don't send the verification email
            verified_email=True)

        self.view_class().send_email(user)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertIn(user.email, sent_mail.to)
        self.assertEqual('example.com password reset', sent_mail.subject)
        self.assertIn('auth/password_reset/confirm/', sent_mail.body)
        self.assertIn('https://', sent_mail.body)


class TestPasswordResetView(APIRequestTestCase):
    view_class = views.PasswordResetView

    def test_options(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('options', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 200)

    def test_put(self):
        old_password = 'old_password'
        new_password = 'new_password'
        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request(
            'put',
            data={'new_password': new_password, 'new_password2': new_password},
            auth=False,
        )
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 200)

        # Get the updated user from the db
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(new_password))

    def test_password_mismatch(self):
        old_password = 'old_password'
        new_password = 'new_password'
        invalid_password = 'different_new_password'
        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request(
            'put',
            data={'new_password': new_password, 'new_password2': invalid_password},
            auth=False,
        )
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 400)

        # Get the updated user from the db
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_put_invalid_user(self):
        # There should never be a user with pk 0
        invalid_uid = urlsafe_base64_encode(b'0')

        request = self.create_request('put', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=invalid_uid)
        self.assertEqual(response.status_code, 404)

    def test_put_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('put', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, 404)


class TestPasswordChangeView(APIRequestTestCase):
    view_class = views.PasswordChangeView

    def test_update(self):
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        request = self.create_request(
            'put',
            user=user,
            data={
                'old_password': old_password,
                'new_password': new_password,
                'new_password2': new_password,
            })
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(new_password))

    def test_update_anonymous(self):
        old_password = 'old_password'
        new_password = 'new_password'

        request = self.create_request(
            'put',
            auth=False,
            data={
                'old_password': old_password,
                'new_password': new_password,
                'new_password2': new_password,
            },
        )
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 401)

    def test_update_wrong_old_password(self):
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        request = self.create_request(
            'put',
            user=user,
            data={
                'old_password': 'invalid_password',
                'new_password': new_password,
                'new_password2': new_password,
            })
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_update_invalid_new_password(self):
        old_password = 'old_password'
        new_password = '2short'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        request = self.create_request(
            'put',
            user=user,
            data={
                'old_password': old_password,
                'new_password': new_password,
                'new_password2': new_password,
            })
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_update_mismatched_passwords(self):
        old_password = 'old_password'
        new_password = 'new_password'
        invalid_password = 'different_new_password'

        user = UserFactory.create()
        user.set_password(old_password)
        user.save()

        request = self.create_request(
            'put',
            user=user,
            data={
                'old_password': old_password,
                'new_password': new_password,
                'new_password2': invalid_password,
            })
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))


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


class TestProfileDetailView(APIRequestTestCase):
    view_class = views.ProfileDetailView

    def expected_data(self, user):
        expected = {
            'name': user.name,
            'email': user.email,
            'date_joined': user.date_joined,
        }
        return expected

    def test_get(self):
        user = UserFactory.build()

        request = self.create_request(user=user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        expected = self.expected_data(user)
        self.assertEqual(response.data, expected)

    def test_get_anonymous(self):
        request = self.create_request(auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 401)

    def test_put(self):
        user = UserFactory.create()
        data = {
            'name': 'New Name',
        }

        request = self.create_request('put', user=user, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        expected = {}
        expected.update(self.expected_data(user))
        expected.update(data)

        self.assertEqual(response.data, expected)

    def test_patch(self):
        user = UserFactory.create()
        data = {
            'name': 'New Name',
        }

        request = self.create_request('patch', user=user, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)

        expected = {}
        expected.update(self.expected_data(user))
        expected.update(data)

        self.assertEqual(response.data, expected)

    def test_options(self):
        request = self.create_request('options')
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
