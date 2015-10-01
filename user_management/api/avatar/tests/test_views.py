from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test.client import Client
from mock import patch
from PIL import Image
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from user_management.api.avatar import views
from user_management.models.tests.factories import AuthTokenFactory, UserFactory
from user_management.models.tests.utils import APIRequestTestCase


User = get_user_model()
TEST_SERVER = 'http://testserver'


def simple_png():
    """Create a 1x1 black png in memory."""
    image_file = BytesIO()
    image = Image.new('RGBA', (1, 1))
    image.save(image_file, 'png')
    image_file._committed = True
    image_file.name = 'test.png'
    image_file.url = '{0}/{1}'.format(
        TEST_SERVER,
        image_file.name
    )
    image_file.seek(0)
    return image_file


class TestProfileAvatar(APIRequestTestCase):
    view_class = views.ProfileAvatar

    def test_get(self):
        user = UserFactory.build(avatar=simple_png())

        request = self.create_request(user=user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar'], simple_png().url)

    def test_get_no_avatar(self):
        user = UserFactory.build()

        request = self.create_request(user=user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar'], None)

    def test_unauthenticated_put(self):
        """
        Test that unauthenticated users cannot put avatars.

        The view should respond with a 401 response, confirming the user
        is unauthorised to put to the view.
        """
        data = {'avatar': simple_png()}
        request = APIRequestFactory().put('/', data=data)
        view = self.view_class.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_put(self):
        user = UserFactory.create()
        data = {'avatar': simple_png()}

        request = APIRequestFactory().put('/', data=data)
        request.user = user
        force_authenticate(request, user)

        view = self.view_class.as_view()
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = 'mocked-url'
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.avatar.read(), simple_png().read())

    def test_options(self):
        request = self.create_request('options')
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_resize(self):
        user = UserFactory.build(avatar=simple_png())

        data = {
            'width': 10,
            'height': 10,
        }
        request = self.create_request(user=user, data=data)
        view = self.view_class.as_view()
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_get_resize_width(self):
        user = UserFactory.build(avatar=simple_png())

        data = {
            'width': 10,
        }
        request = self.create_request(user=user, data=data)
        view = self.view_class.as_view()
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_get_resize_height(self):
        user = UserFactory.build(avatar=simple_png())

        data = {
            'height': 10,
        }
        request = self.create_request(user=user, data=data)
        view = self.view_class.as_view()
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_delete_without_avatar(self):
        user = UserFactory.create()
        request = self.create_request('delete', user=user)
        view = self.view_class.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_with_avatar(self):
        user = UserFactory.create(avatar=simple_png())
        request = self.create_request('delete', user=user)
        view = self.view_class.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user = User.objects.get(pk=user.pk)
        self.assertFalse(user.avatar)

    def test_send_without_token_header(self):
        """Test support for legacy browsers that cannot support AJAX uploads.

        This shows three things:
         - users can authenticate by submitting the token in the form data.
         - users can use a POST fallback.
         - csrf is not required (the token is equivalent).
        """
        client = Client(enforce_csrf_checks=True)
        user = UserFactory.create()
        token = AuthTokenFactory(user=user)

        data = {'avatar': simple_png(), 'token': token.key}
        url = reverse('user_management_api:profile_avatar')
        response = client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('avatar', response.data)


class TestUserAvatar(APIRequestTestCase):
    view_class = views.UserAvatar

    def setUp(self):
        self.user = UserFactory.build()
        self.other_user = UserFactory.build(avatar=simple_png())

    def get_response(self, request):
        """
        Create a response object by patching view_class.get_object to return
        self.other_user, allowing self.other_user to not be saved.
        """
        view = self.view_class.as_view()
        with patch.object(self.view_class, 'get_object') as get_object:
            get_object.return_value = self.other_user
            response = view(request)
        return response

    def check_method_forbidden(self, method):
        request = self.create_request(method, user=self.user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_anonymous(self):
        request = self.create_request(auth=False)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_unauthorised(self):
        self.check_method_forbidden('post')

    def test_put_unauthorised(self):
        self.check_method_forbidden('put')

    def test_patch_unauthorised(self):
        self.check_method_forbidden('patch')

    def test_delete_unauthorised(self):
        self.check_method_forbidden('delete')

    def test_delete_not_allowed(self):
        """ Tests DELETE user for staff not allowed"""
        self.user.is_staff = True
        request = self.create_request('delete', user=self.user)
        view = self.view_class.as_view()
        response = view(request)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_get(self):
        request = self.create_request(user=self.user)
        response = self.get_response(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar'], simple_png().url)

    def test_get_no_avatar(self):
        self.other_user.avatar = None
        request = self.create_request(user=self.user)
        response = self.get_response(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['avatar'], None)

    def test_get_resize(self):
        data = {
            'width': 10,
            'height': 10,
        }
        request = self.create_request(user=self.user, data=data)
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = self.get_response(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_get_resize_width(self):
        data = {
            'width': 10,
        }
        request = self.create_request(user=self.user, data=data)
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = self.get_response(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_get_resize_height(self):
        data = {
            'height': 10,
        }
        request = self.create_request(user=self.user, data=data)
        expected_url = 'mocked-url'
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = expected_url
            response = self.get_response(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['avatar'], expected_url)

    def test_put(self):
        user = UserFactory.build(is_staff=True)
        other_user = UserFactory.create()
        data = {'avatar': simple_png()}

        request = APIRequestFactory().put('/', data=data)
        request.user = user
        force_authenticate(request, user)

        view = self.view_class.as_view()
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = 'mocked-url'
            response = view(request, pk=other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=other_user.pk)
        self.assertEqual(user.avatar.read(), simple_png().read())

    def test_patch(self):
        user = UserFactory.build(is_staff=True)
        other_user = UserFactory.create()
        data = {'avatar': simple_png()}

        request = APIRequestFactory().patch('/', data=data)
        request.user = user
        force_authenticate(request, user)

        view = self.view_class.as_view()
        with patch('django.core.files.storage.Storage.url') as mocked_url:
            mocked_url.return_value = 'mocked-url'
            response = view(request, pk=other_user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=other_user.pk)
        self.assertEqual(user.avatar.read(), simple_png().read())

    def test_send_without_token_header(self):
        """Test support for legacy browsers that cannot support AJAX uploads.

        This shows three things:
         - users can authenticate by submitting the token in the form data.
         - users can use a POST fallback.
         - csrf is not required (the token is equivalent).
        """
        client = Client(enforce_csrf_checks=True)
        user = UserFactory.create(is_staff=True)
        token = AuthTokenFactory(user=user)

        data = {'avatar': simple_png(), 'token': token.key}
        url_kwargs = {'pk': user.pk}
        url = reverse('user_management_api:user_avatar', kwargs=url_kwargs)
        response = client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('avatar', response.data)
