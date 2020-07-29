from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestURLs(URLTestCase):
    """Ensure the urls work."""

    def test_profile_avatar_url(self):
        self.assert_url_matches_view(
            view=views.ProfileAvatar,
            expected_url='/profile/avatar',
            url_name='user_management_api_avatar:profile_avatar')

    def test_user_avatar_url(self):
        self.assert_url_matches_view(
            view=views.UserAvatar,
            expected_url='/users/1/avatar',
            url_name='user_management_api_avatar:user_avatar',
            url_kwargs={'pk': 1})
