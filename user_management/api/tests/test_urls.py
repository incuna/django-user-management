from incuna_test_utils.testcases.urls import URLsTestCase

from .. import views


class TestURLs(URLsTestCase):
    """Ensure the urls work."""

    def test_auth_token_url(self):
        self.check_url(
            view_class=views.GetToken,
            expected_url='/auth',
            url_name='user_management_api:auth')

    def test_password_reset_confirm_url(self):
        self.check_url(
            view_class=views.PasswordReset,
            expected_url='/auth/password_reset/confirm/a/x-y',
            url_name='user_management_api:password_reset_confirm',
            url_kwargs={'uidb64': 'a', 'token': 'x-y'})

    def test_password_reset_url(self):
        self.check_url(
            view_class=views.PasswordResetEmail,
            expected_url='/auth/password_reset',
            url_name='user_management_api:password_reset')

    def test_profile_detail_url(self):
        self.check_url(
            view_class=views.ProfileDetail,
            expected_url='/profile',
            url_name='user_management_api:profile_detail')

    def test_password_change_url(self):
        self.check_url(
            view_class=views.PasswordChange,
            expected_url='/profile/password',
            url_name='user_management_api:password_change')

    def test_register_url(self):
        self.check_url(
            view_class=views.UserRegister,
            expected_url='/register',
            url_name='user_management_api:register')

    def test_user_detail_url(self):
        self.check_url(
            view_class=views.UserDetail,
            expected_url='/users/1',
            url_name='user_management_api:user_detail',
            url_kwargs={'pk': 1})

    def test_user_list_url(self):
        self.check_url(
            view_class=views.UserList,
            expected_url='/users',
            url_name='user_management_api:user_list')
