from django.core.urlresolvers import resolve, reverse
from django.test import TestCase


class TestURLs(TestCase):
    """Ensure the urls work."""
    def test_auth_token_url(self):
        url = reverse('auth')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'GetToken')

    def test_password_reset_confirm_url(self):
        url = reverse('password_reset_confirm', kwargs={'uidb64': 'a', 'token': 'x-y'})
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'PasswordResetView')

    def test_password_reset_url(self):
        url = reverse('password_reset')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'PasswordResetEmailView')

    def test_profile_detail_url(self):
        url = reverse('profile_detail')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'ProfileDetailView')

    def test_password_change_url(self):
        url = reverse('password_change')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'PasswordChangeView')

    def test_register_url(self):
        url = reverse('register')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'UserRegister')

    def test_user_detail_url(self):
        url = reverse('user_detail', kwargs={'pk': 1})
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'UserDetailView')

    def test_user_list_url(self):
        url = reverse('user_list')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'UserListView')
