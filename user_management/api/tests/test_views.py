from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from mock import patch
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

from user_management.api import views
from user_management.models.tests.factories import UserFactory
from user_management.models.tests.models import BasicUser
from user_management.models.tests.utils import APIRequestTestCase


User = get_user_model()
TEST_SERVER = 'http://testserver'


class GetTokenTest(APIRequestTestCase):
    view_class = views.GetToken

    def tearDown(self):
        cache.clear()

    def test_post(self):
        username = 'Test@example.com'
        password = 'myepicstrongpassword'
        UserFactory.create(email=username.lower(), password=password, is_active=True)

        data = {'username': username, 'password': password}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

    def test_post_username(self):
        username = 'Test@example.com'
        password = 'myepicstrongpassword'
        UserFactory.create(email=username, password=password, is_active=True)

        data = {'username': username.lower(), 'password': password}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)

    def test_delete(self):
        user = UserFactory.create()
        token = Token.objects.create(user=user)

        request = self.create_request('delete', user=user)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(pk=token.pk)

    def test_delete_no_token(self):
        request = self.create_request('delete')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_default_user_auth_throttle(self):
        default_rate = 10
        auth_url = reverse('user_management_api:auth')
        expected_status = status.HTTP_429_TOO_MANY_REQUESTS

        request = APIRequestFactory().get(auth_url)
        view = self.view_class.as_view()

        # make all but one of our allowed requests
        for i in range(default_rate - 1):
            view(request)

        response = view(request)  # our last allowed request
        self.assertNotEqual(response.status_code, expected_status)

        response = view(request)  # our throttled request
        self.assertEqual(response.status_code, expected_status)

    @patch('rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES', new={
        'logins': '1/minute',
    })
    def test_user_auth_throttle(self):
        auth_url = reverse('user_management_api:auth')
        expected_status = status.HTTP_429_TOO_MANY_REQUESTS

        request = APIRequestFactory().get(auth_url)

        response = self.view_class.as_view()(request)
        self.assertNotEqual(response.status_code, expected_status)

        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, expected_status)


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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_post(self):
        """Unauthenticated Users should be able to register."""
        request = self.create_request('post', auth=False, data=self.data)

        send_email_path = 'user_management.models.mixins.VerifyEmailMixin.send_validation_email'
        with patch(send_email_path) as send:
            response = self.view_class.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        send.assert_called_once_with()

        user = User.objects.get()
        self.assertEqual(user.name, self.data['name'])
        self.assertEqual(user.email, self.data['email'])
        # Should be hash, not literal password
        self.assertNotEqual(user.password, self.data['password'])

        # Password should validate
        self.assertTrue(check_password(self.data['password'], user.password))

    @patch('user_management.api.serializers.RegistrationSerializer.Meta.model',
           new=BasicUser)
    def test_unauthenticated_user_post_no_verify_email(self):
        """An email should not be sent if email_verification_required is False."""
        request = self.create_request('post', auth=False, data=self.data)

        send_email_path = 'user_management.models.mixins.VerifyEmailMixin.send_validation_email'
        with patch(send_email_path) as send:
            response = self.view_class.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(send.called)

    def test_post_with_missing_data(self):
        """Password should not be sent back on failed request."""
        self.data.pop('name')
        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('name' in response.data)
        self.assertFalse('password' in response.data)
        self.assertFalse(User.objects.count())

    def test_post_password_mismatch(self):
        """Password and password2 should be the same."""
        self.data['password2'] = 'something_different'
        request = self.create_request('post', auth=False, data=self.data)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue('email' in response.data, msg=response.data)

        self.assertFalse(User.objects.count() > 1)


class TestPasswordResetEmail(APIRequestTestCase):
    view_class = views.PasswordResetEmail

    def tearDown(self):
        cache.clear()

    def test_existent_email(self):
        email = 'exists@example.com'
        user = UserFactory.create(email=email)

        request = self.create_request('post', data={'email': email}, auth=False)
        view = self.view_class.as_view()
        with patch.object(self.view_class, 'send_email') as send_email:
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        send_email.assert_called_once_with(user)

    def test_authenticated(self):
        request = self.create_request('post', auth=True)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_existent_email(self):
        email = 'doesnotexist@example.com'
        UserFactory.create(email='exists@example.com')

        request = self.create_request('post', data={'email': email}, auth=False)
        view = self.view_class.as_view()
        with patch.object(self.view_class, 'send_email') as send_email:
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(send_email.called)

    def test_missing_email(self):
        request = self.create_request('post', auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_email(self):
        email = 'test@example.com'
        user = UserFactory.create(
            email=email,
            # Don't send the verification email
            email_verification_required=False,
        )

        self.view_class().send_email(user)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertIn(user.email, sent_mail.to)
        self.assertEqual('example.com password reset', sent_mail.subject)
        self.assertIn('auth/password_reset/confirm/', sent_mail.body)
        self.assertIn('https://', sent_mail.body)

    def test_options(self):
        """Ensure information about email field is included in options request"""
        request = self.create_request('options', auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_post_options = {
            'email': {
                'type': 'email',
                'required': True,
                'read_only': False,
                'label': 'Email address',
                'max_length': 511,
            },
        }
        self.assertEqual(
            response.data['actions']['POST'],
            expected_post_options,
        )

    def test_default_user_password_reset_throttle(self):
        default_rate = 3
        auth_url = reverse('user_management_api:password_reset')
        expected_status = status.HTTP_429_TOO_MANY_REQUESTS

        request = APIRequestFactory().get(auth_url)
        view = self.view_class.as_view()

        # make all but one of our allowed requests
        for i in range(default_rate - 1):
            view(request)

        response = view(request)  # our last allowed request
        self.assertNotEqual(response.status_code, expected_status)

        response = view(request)  # our throttled request
        self.assertEqual(response.status_code, expected_status)

    @patch('rest_framework.throttling.ScopedRateThrottle.THROTTLE_RATES', new={
        'passwords': '1/minute',
    })
    def test_user_password_reset_throttle(self):
        auth_url = reverse('user_management_api:password_reset')
        expected_status = status.HTTP_429_TOO_MANY_REQUESTS

        request = APIRequestFactory().get(auth_url)

        response = self.view_class.as_view()(request)
        self.assertNotEqual(response.status_code, expected_status)

        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, expected_status)


class TestPasswordReset(APIRequestTestCase):
    view_class = views.PasswordReset

    def test_options(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('options', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        old_password = 'old_password'
        new_password = 'new_password'
        user = UserFactory.create(password=old_password)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request(
            'put',
            data={'new_password': new_password, 'new_password2': new_password},
            auth=False,
        )
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Get the updated user from the db
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(new_password))

    def test_password_mismatch(self):
        old_password = 'old_password'
        new_password = 'new_password'
        invalid_password = 'different_new_password'
        user = UserFactory.create(password=old_password)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request(
            'put',
            data={'new_password': new_password, 'new_password2': invalid_password},
            auth=False,
        )
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Get the updated user from the db
        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_put_invalid_user(self):
        # There should never be a user with pk 0
        invalid_uid = urlsafe_base64_encode(b'0')

        request = self.create_request('put', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=invalid_uid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('put', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_stack_wrong_url(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(b'0')  # Invalid uid, therefore bad url

        view_name = 'user_management_api:password_reset_confirm'
        url = reverse(view_name, kwargs={'uidb64': uid, 'token': token})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(hasattr(response, 'accepted_renderer'))


class TestPasswordChange(APIRequestTestCase):
    view_class = views.PasswordChange

    def test_update(self):
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.create(password=old_password)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_wrong_old_password(self):
        old_password = 'old_password'
        new_password = 'new_password'

        user = UserFactory.create(password=old_password)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_update_invalid_new_password(self):
        old_password = 'old_password'
        new_password = '2short'

        user = UserFactory.create(password=old_password)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(pk=user.pk)
        self.assertTrue(user.check_password(old_password))

    def test_update_mismatched_passwords(self):
        old_password = 'old_password'
        new_password = 'new_password'
        invalid_password = 'different_new_password'

        user = UserFactory.create(password=old_password)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        updated_user = User.objects.get(pk=user.pk)
        self.assertFalse(updated_user.email_verification_required)
        self.assertTrue(updated_user.is_active)

    def test_post_unauthenticated(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        updated_user = User.objects.get(pk=user.pk)
        self.assertFalse(updated_user.email_verification_required)
        self.assertTrue(updated_user.is_active)

    def test_post_invalid_user(self):
        # There should never be a user with pk 0
        invalid_uid = urlsafe_base64_encode(b'0')

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=invalid_uid)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_verified_email(self):
        user = UserFactory.create(email_verification_required=False)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_different_user_logged_in(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post', user=other_user)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        updated_user = User.objects.get(pk=user.pk)
        self.assertFalse(updated_user.email_verification_required)

        logged_in_user = User.objects.get(pk=other_user.pk)
        self.assertTrue(logged_in_user.email_verification_required)

    def test_full_stack_wrong_url(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(b'0')  # Invalid uid, therefore bad url

        view_name = 'user_management_api:verify_user'
        url = reverse(view_name, kwargs={'uidb64': uid, 'token': token})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(hasattr(response, 'accepted_renderer'))


class TestProfileDetail(APIRequestTestCase):
    view_class = views.ProfileDetail

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = self.expected_data(user)
        self.assertEqual(response.data, expected)

    def test_get_anonymous(self):
        request = self.create_request(auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put(self):
        user = UserFactory.create()
        data = {
            'name': 'New Name',
        }

        request = self.create_request('put', user=user, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {}
        expected.update(self.expected_data(user))
        expected.update(data)

        self.assertEqual(response.data, expected)

    def test_options(self):
        request = self.create_request('options')
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestUserList(APIRequestTestCase):
    view_class = views.UserList

    def expected_data(self, user):
        url = reverse('user_management_api:user_detail', kwargs={'pk': user.pk})
        expected = {
            'url': TEST_SERVER + url,
            'name': user.name,
            'email': user.email,
            'date_joined': user.date_joined,
        }
        return expected

    def test_get_anonymous(self):
        request = self.create_request(auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get(self):
        user = UserFactory.create()

        request = self.create_request(user=user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = [self.expected_data(user)]
        self.assertEqual(response.data, expected)

    def test_option(self):
        request = self.create_request('options')
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post(self):
        """Users should be able to create."""
        data = {
            'name': "Robert'); DROP TABLE Students;--'",
            'email': 'Bobby.Tables+327@xkcd.com',
        }
        request = self.create_request('post', auth=True, data=data)
        request.user.is_staff = True
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=data['email'].lower())
        self.assertEqual(user.name, data['name'])

    def test_post_unauthorised(self):
        request = self.create_request('post', auth=True)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestUserDetail(APIRequestTestCase):
    view_class = views.UserDetail

    def setUp(self):
        self.user, self.other_user = UserFactory.create_batch(2)

    def expected_data(self, user):
        url = reverse('user_management_api:user_detail', kwargs={'pk': user.pk})
        expected = {
            'url': TEST_SERVER + url,
            'name': user.name,
            'email': user.email,
            'date_joined': user.date_joined,
        }
        return expected

    def check_method_forbidden(self, method):
        request = self.create_request(method, user=self.user)
        view = self.view_class.as_view()
        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        request = self.create_request(user=self.user)
        view = self.view_class.as_view()
        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = self.expected_data(self.other_user)
        self.assertEqual(response.data, expected)

    def test_get_anonymous(self):
        request = self.create_request(auth=False)
        view = self.view_class.as_view()
        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_unauthorised(self):
        self.check_method_forbidden('post')

    def test_put_unauthorised(self):
        self.check_method_forbidden('put')

    def test_patch_unauthorised(self):
        self.check_method_forbidden('patch')

    def test_delete_unauthorised(self):
        self.check_method_forbidden('delete')

    def test_put(self):
        """ Tests PUT existing user for staff """
        self.user.is_staff = True

        data = {'name': 'Jean Dujardin'}

        request = self.create_request('put', user=self.user, data=data)

        view = self.view_class.as_view()

        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        user = User.objects.get(pk=self.other_user.pk)
        self.assertEqual(user.name, data['name'])

    def test_patch(self):
        """ Tests PATCH new user for staff """
        self.user.is_staff = True

        data = {'name': 'Jean Deschamps'}

        request = self.create_request('patch', user=self.user, data=data)

        view = self.view_class.as_view()

        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        user = User.objects.get(pk=self.other_user.pk)
        self.assertEqual(user.name, data['name'])

    def test_delete(self):
        """ Tests DELETE user for staff """
        self.user.is_staff = True

        request = self.create_request('delete', user=self.user)

        view = self.view_class.as_view()

        response = view(request, pk=self.other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user = User.objects.get()
        self.assertEqual(self.user, user)
