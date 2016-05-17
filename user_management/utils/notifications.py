import incuna_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from pigeon.notification import Notification


def password_reset_email_context(notification):
    """Email context to reset a user password."""
    return {
        'protocol': 'https',
        'uid': notification.user.generate_uid(),
        'token': notification.user.generate_token(),
        'site': notification.site,
    }


def validation_email_context(notification):
    """Email context to verify a user email."""
    return {
        'protocol': 'https',
        'token': notification.user.generate_validation_token(),
        'site': notification.site,
    }


def email_handler(notification, email_context):
    """Send a notification by email."""
    incuna_mail.send(
        to=notification.user.email,
        subject=notification.email_subject,
        template_name=notification.text_email_template,
        html_template_name=notification.html_email_template,
        context=email_context(notification),
        headers=getattr(notification, 'headers', {}),
    )


def password_reset_email_handler(notification):
    """Password reset email handler."""
    base_subject = _('{domain} password reset').format(domain=notification.site.domain)
    subject = getattr(settings, 'DUM_PASSWORD_RESET_SUBJECT', base_subject)
    notification.email_subject = subject
    email_handler(notification, password_reset_email_context)


def validation_email_handler(notification):
    """Validation email handler."""
    base_subject = _('{domain} account validate').format(domain=notification.site.domain)
    subject = getattr(settings, 'DUM_VALIDATE_EMAIL_SUBJECT', base_subject)
    notification.email_subject = subject
    email_handler(notification, validation_email_context)


class PasswordResetNotification(Notification):
    """`PasswordResetNotification` defines text and html email templates."""
    handlers = (password_reset_email_handler,)
    text_email_template = 'user_management/password_reset_email.txt'
    html_email_template = 'user_management/password_reset_email.html'


class ValidationNotification(Notification):
    """`ValidationNotification` defines text and html email templates."""
    handlers = (validation_email_handler,)
    text_email_template = 'user_management/account_validation_email.txt'
    html_email_template = 'user_management/account_validation_email.html'
