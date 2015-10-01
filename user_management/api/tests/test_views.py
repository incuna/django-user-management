import datetime
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from mock import patch
from rest_framework import status
from rest_framework.test import APIRequestFactory

from user_management.api import models, views
from user_management.api.tests.test_throttling import THROTTLE_RATE_PATH
from user_management.models.tests.factories import AuthTokenFactory, UserFactory
from user_management.models.tests.models import BasicUser
from user_management.models.tests.utils import APIRequestTestCase


User = get_user_model()
TEST_SERVER = 'http://testserver'
SEND_METHOD = 'user_management.utils.notifications.incuna_mail.send'
EMAIL_CONTEXT = 'user_management.utils.notifications.email_context'


class GetAuthTokenTest(APIRequestTestCase):
    model = models.AuthToken
    view_class = views.GetAuthToken

    def setUp(self):
        self.username = 'Test@example.com'
        self.password = 'myepicstrongpassword'
        self.data = {'username': self.username, 'password': self.password}

    def tearDown(self):
        cache.clear()

    def test_post(self):
        """Assert user can sign in"""
        UserFactory.create(email=self.username, password=self.password)

        request = self.create_request('post', auth=False, data=self.data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK, msg=response.data)

        # Ensure user has a token now
        token = self.model.objects.get()
        self.assertEqual(response.data['token'], token.key)

    def test_post_non_existing_user(self):
        """Assert non existing raises an error."""
        request = self.create_request('post', auth=False, data=self.data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=response.data,
        )
        expected = 'Unable to log in with provided credentials.'
        self.assertIn(expected, response.data['non_field_errors'])
        self.assertNotIn('token', response.data)

    def test_post_user_not_confirmed(self):
        """Assert non active users can not log in."""
        UserFactory.create(email=self.username, password=self.password, is_active=False)

        request = self.create_request('post', auth=False, data=self.data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=response.data,
        )
        expected = 'User account is disabled.'
        self.assertIn(expected, response.data['non_field_errors'])
        self.assertNotIn('token', response.data)

    def test_post_no_data(self):
        """Assert sending no data raise an error."""
        data = {'username': None, 'password': None}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=response.data,
        )
        expected = 'This field is required.'
        self.assertIn(expected, response.data['username'])
        self.assertIn(expected, response.data['password'])
        self.assertNotIn('token', response.data)

    def test_delete(self):
        someday = timezone.now() + datetime.timedelta(days=1)
        user = UserFactory.create()
        token = AuthTokenFactory.create(user=user, expires=someday)

        # Custom auth header containing token
        auth = 'Token ' + token.key
        request = self.create_request(
            'delete',
            user=user,
            HTTP_AUTHORIZATION=auth,
        )
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(self.model.DoesNotExist):
            self.model.objects.get(pk=token.pk)

    def test_delete_no_token(self):
        request = self.create_request('delete')
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_invalid_token(self):
        # token is incomplete
        auth = 'Token'
        request = self.create_request(
            'delete',
            HTTP_AUTHORIZATION=auth,
        )
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_spacious_token(self):
        # token has too many whitespaces
        auth = 'Token yolo jimmy'
        request = self.create_request(
            'delete',
            HTTP_AUTHORIZATION=auth,
        )
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_token(self):
        """An unknown token is accepted silently."""
        auth = 'Token unknown'
        request = self.create_request('delete', HTTP_AUTHORIZATION=auth)
        response = self.view_class.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_auth_method_not_allowed(self):
        """Ensure GET requests are not allowed."""
        auth_url = reverse('user_management_api:auth')
        request = APIRequestFactory().get(auth_url)
        response = self.view_class.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


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

        response = self.view_class.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        verify_url_regex = re.compile(
            r'''
                https://example\.com/\#/register/verify/
                [0-9A-Za-z_\-]+/  # uid
                [0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/  # token
            ''',
            re.VERBOSE,
        )
        self.assertRegex(email.body, verify_url_regex)
        html_email = email.alternatives[0][0]
        self.assertRegex(html_email, verify_url_regex)

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
        """
        An email should not be sent if email_verification_required is False.
        """
        request = self.create_request('post', auth=False, data=self.data)

        response = self.view_class.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 0)

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
        self.assertIn('Your passwords do not match.', response.data['password2'])

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

        self.assertEqual(User.objects.count(), 1)


class TestPasswordResetEmail(APIRequestTestCase):
    view_class = views.PasswordResetEmail

    def tearDown(self):
        cache.clear()

    def test_existent_email(self):
        email = 'exists@example.com'
        user = UserFactory.create(email=email)
        context = {}
        site = Site.objects.get_current()

        request = self.create_request(
            'post',
            data={'email': email},
            auth=False,
        )
        view = self.view_class.as_view()
        with patch(EMAIL_CONTEXT) as get_context:
            get_context.return_value = context
            with patch(SEND_METHOD) as send_email:
                response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        expected = {
            'to': user.email,
            'template_name': 'user_management/password_reset_email.txt',
            'html_template_name': 'user_management/password_reset_email.html',
            'subject': '{} password reset'.format(site.domain),
            'context': context,
        }
        send_email.assert_called_once_with(**expected)

    def test_authenticated(self):
        request = self.create_request('post', auth=True)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_existent_email(self):
        email = 'doesnotexist@example.com'
        UserFactory.create(email='exists@example.com')

        request = self.create_request(
            'post',
            data={'email': email},
            auth=False,
        )
        view = self.view_class.as_view()
        with patch(SEND_METHOD) as send_email:
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(send_email.called)

    def test_missing_email(self):
        request = self.create_request('post', auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_content(self):
        """Assert email content is output correctly."""
        email = 'exists@example.com'
        user = UserFactory.create(email=email)

        request = self.create_request(
            'post',
            data={'email': email},
            auth=False,
        )
        view = self.view_class.as_view()
        view(request)

        self.assertEqual(len(mail.outbox), 1)

        sent_mail = mail.outbox[0]
        self.assertIn(user.email, sent_mail.to)
        self.assertEqual('example.com password reset', sent_mail.subject)
        self.assertIn('auth/password_reset/confirm/', sent_mail.body)
        self.assertIn('https://', sent_mail.body)

    def test_options(self):
        """
        Ensure information about email field is included in options request.

        Ensure that the options request isn't rate limited.
        """
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

    def test_options_delimit(self):
        """
        Ensure information about email field is included in options request.

        Ensure that the options request isn't rate limited.
        """
        request = self.create_request('options', auth=False)
        view = self.view_class.as_view()
        default_rate = 3
        # First three requests
        for i in range(default_rate):
            view(request)

        # Assert fourth request is not throttled
        response = view(request)
        self.assertNotEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )


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
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'
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
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'
        invalid_password = 'different_new_password'
        user = UserFactory.create(password=old_password)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request(
            'put',
            data={
                'new_password': new_password,
                'new_password2': invalid_password,
            },
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('put', auth=False)
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_full_stack_wrong_url(self):
        user = UserFactory.create()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(b'0')  # Invalid uid, therefore bad url

        view_name = 'user_management_api:password_reset_confirm'
        url = reverse(view_name, kwargs={'uidb64': uid, 'token': token})
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertTrue(hasattr(response, 'accepted_renderer'))


class TestPasswordChange(APIRequestTestCase):
    view_class = views.PasswordChange

    def test_update(self):
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'

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
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'

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
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'

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
        old_password = '0ld_passworD'
        new_password = '2Short'

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
        old_password = '0ld_passworD'
        new_password = 'n3w_Password'
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_invalid_token(self):
        user = UserFactory.create()
        other_user = UserFactory.create()
        token = default_token_generator.make_token(other_user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        request = self.create_request('post')
        view = self.view_class.as_view()
        response = view(request, uidb64=uid, token=token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_delete(self):
        """Assert a user can delete its profile."""
        request = self.create_request('delete')
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get()


class TestUserList(APIRequestTestCase):
    view_class = views.UserList

    def expected_data(self, user):
        url = reverse(
            'user_management_api:user_detail',
            kwargs={'pk': user.pk},
        )
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
        url = reverse(
            'user_management_api:user_detail',
            kwargs={'pk': user.pk},
        )
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
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        user = User.objects.get(pk=self.other_user.pk)
        self.assertEqual(user.name, data['name'])

    def test_patch(self):
        """ Tests PATCH new user for staff """
        self.user.is_staff = True

        data = {'name': 'Jean Deschamps'}

        request = self.create_request('patch', user=self.user, data=data)

        view = self.view_class.as_view()

        response = view(request, pk=self.other_user.pk)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

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


@patch(THROTTLE_RATE_PATH, new={'confirmations': '4/minute'})
class ResendConfirmationEmailTest(APIRequestTestCase):
    """Assert `ResendConfirmationEmail` behaves properly."""
    view_class = views.ResendConfirmationEmail

    def test_post(self):
        """Assert user can request a new confirmation email."""
        user = UserFactory.create()
        data = {'email': user.email}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            msg=response.data,
        )

    def test_post_unknown_email(self):
        """Assert unknown email raises an error."""
        data = {'email': 'theman@theiron.mask'}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_post_email_already_verified(self):
        """Assert email already verified does not trigger another email."""
        user = UserFactory.create(email_verification_required=False)
        data = {'email': user.email}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_send_email(self):
        """Assert user can receive a new confirmation email."""
        user = UserFactory.create()
        data = {'email': user.email}
        request = self.create_request('post', auth=False, data=data)
        view = self.view_class.as_view()
        view(request)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]

        self.assertIn(user.email, email.to)
        expected = 'https://example.com/#/register/verify/'
        self.assertIn(expected, email.body)

        expected = 'example.com account validate'
        self.assertEqual(email.subject, expected)
