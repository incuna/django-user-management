from django.core.urlresolvers import resolve, reverse
from django.test import TestCase


class TestURLs(TestCase):
    """Ensure the urls work."""
    def test_auth_token_url(self):
        url = reverse('auth')
        view_name = resolve(url).func.__name__
        self.assertEqual(view_name, 'GetToken')
