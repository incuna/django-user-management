import datetime

from django.core.management.base import BaseCommand

from user_management.api.models import AuthToken


class Command(BaseCommand):
    help = "Remove expired auth tokens from the database."

    def handle(self, *args, **options):
        now = datetime.datetime.now()

        AuthToken.objects.filter(expires__lte=now).delete()
