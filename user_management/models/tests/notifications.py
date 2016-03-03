from user_management.utils.notifications import PasswordResetNotification


class CustomPasswordResetNotification(PasswordResetNotification):
    """Test setting a custom notification to alter how we send the password reset."""
    text_email_template = 'my_custom_email.txt'
    html_email_template = None
    headers = {'test-header': 'Test'}
