from django.core.management.base import BaseCommand
from django.utils import timezone

from user_management.api.models import AuthToken


class Command(BaseCommand):
    help = "Remove expired auth tokens from the database."

    def handle(self, *args, **options):
        now = timezone.now()
        AuthToken.objects.filter(expires__lte=now).delete()
