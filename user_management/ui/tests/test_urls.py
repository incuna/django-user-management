from incuna_test_utils.testcases.urls import URLTestCase

from .. import views


class TestURLs(URLTestCase):
    def test_password_reset_confirm_url(self):
        self.assert_url_matches_view(
            view=views.VerifyUserEmailView,
            expected_url='/register/verify/x:-y/',
            url_name='user_management_ui:registration-verify',
            url_kwargs={'token': 'x:-y'},
        )
