import incuna_mail
from pigeon.notification import Notification as NotificationBase


def email_handler(notification):
    """Send a notification by email."""
    incuna_mail.send(
        to=notification.user.email,
        subject=notification.email_subject,
        template_name=notification.text_email_template,
        html_template_name=notification.html_email_template,
        context=notification.context,
    )


class Notification(NotificationBase):
    handlers = (email_handler,)
