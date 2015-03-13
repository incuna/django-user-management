import incuna_mail
from pigeon.notification import Notification


def email_handler(notification):
    """Send a notification by email."""
    incuna_mail.send(
        to=notification.user.email,
        subject=notification.email_subject,
        template_name=notification.text_email_template,
        html_template_name=notification.html_email_template,
        context=notification.context,
    )


class NotificationBase(Notification):
    """Base notification class defining an `email_handler`."""
    handlers = (email_handler,)


class PasswordResetNotification(NotificationBase):
    """`PasswordResetNotification` defines text and html email templates."""
    text_email_template = 'user_management/password_reset_email.txt'
    html_email_template = 'user_management/password_reset_email.html'


class ValidationNotification(NotificationBase):
    """`ValidationNotification` defines text and html email templates."""
    text_email_template = 'user_management/account_validation_email.txt'
    html_email_template = 'user_management/account_validation_email.html'
