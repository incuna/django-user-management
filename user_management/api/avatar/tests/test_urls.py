from incuna_test_utils.testcases.urls import URLsTestCase

from .. import views


class TestURLs(URLsTestCase):
    """Ensure the urls work."""

    def test_profile_avatar_url(self):
        self.check_url(
            view_class=views.ProfileAvatar,
            expected_url='/profile/avatar',
            url_name='user_management_api:profile_avatar')

    def test_user_avatar_url(self):
        self.check_url(
            view_class=views.UserAvatar,
            expected_url='/users/1/avatar',
            url_name='user_management_api:user_avatar',
            url_kwargs={'pk': 1})
