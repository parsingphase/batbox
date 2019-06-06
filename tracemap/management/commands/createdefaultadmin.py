from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User  # Default model
from django.db import DEFAULT_DB_ALIAS
import random
import string


# Create a default admin user (See createsuperuser.py) with a default,
# random password dumped in a specified file

class Command(BaseCommand):
    help = 'Create a default admin for local use'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()  # type: User
        self.username_field = self.UserModel._meta.get_field(
            self.UserModel.USERNAME_FIELD
        )

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', type=str, help=''
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        username = 'admin'
        email = 'admin@example.com'
        password = ''.join(
            random.sample(string.ascii_letters + string.digits, 12)
        )
        existing = self.UserModel.objects.filter(username=username)
        if len(existing) > 0:
            print('Admin already created')
            quit(0)

        # createsuperuser command does it, we're just extending the hack
        # noinspection PyUnresolvedReferences
        self.UserModel._default_manager.db_manager(
            DEFAULT_DB_ALIAS
        ).create_superuser(
            username=username, password=password, email=email
        )

        print(f"Created superuser '{username}', password is in " + filename)
        with open(filename, 'w') as fh:
            print(password, file=fh)
