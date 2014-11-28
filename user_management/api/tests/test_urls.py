from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestURLs(URLTestCase):
    """Ensure the urls work."""

    def test_auth_token_url(self):
        self.assert_url_matches_view(
            view=views.GetAuthToken,
            expected_url='/auth',
            url_name='user_management_api:auth')

    def test_password_reset_confirm_url(self):
        self.assert_url_matches_view(
            view=views.PasswordReset,
            expected_url='/auth/password_reset/confirm/a/x-y',
            url_name='user_management_api:password_reset_confirm',
            url_kwargs={'uidb64': 'a', 'token': 'x-y'})

    def test_password_reset_url(self):
        self.assert_url_matches_view(
            view=views.PasswordResetEmail,
            expected_url='/auth/password_reset',
            url_name='user_management_api:password_reset')

    def test_profile_detail_url(self):
        self.assert_url_matches_view(
            view=views.ProfileDetail,
            expected_url='/profile',
            url_name='user_management_api:profile_detail')

    def test_password_change_url(self):
        self.assert_url_matches_view(
            view=views.PasswordChange,
            expected_url='/profile/password',
            url_name='user_management_api:password_change')

    def test_register_url(self):
        self.assert_url_matches_view(
            view=views.UserRegister,
            expected_url='/register',
            url_name='user_management_api:register')

    def test_user_detail_url(self):
        self.assert_url_matches_view(
            view=views.UserDetail,
            expected_url='/users/1',
            url_name='user_management_api:user_detail',
            url_kwargs={'pk': 1})

    def test_user_list_url(self):
        self.assert_url_matches_view(
            view=views.UserList,
            expected_url='/users',
            url_name='user_management_api:user_list')
