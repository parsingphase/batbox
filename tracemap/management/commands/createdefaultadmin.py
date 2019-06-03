from django.core.management.base import BaseCommand


# Create a default admin user (See createsuperuser.py) with a default, random password dumped in a specified file

class Command(BaseCommand):
    help = 'Create a default admin for local use'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', type=str, help=''
        )

    def handle(self, *args, **kwargs):
        pass
