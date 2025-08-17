from django.core.management.base import BaseCommand

from apps.system_setting.seed_data import seed_system_color, seed_system_setting, seed_social_media, seed_smtp_credentials
from apps.users.seed_users import seed_users


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        seed_users()
        seed_system_setting()
        seed_social_media()
        seed_smtp_credentials()
        seed_system_color()

        self.stdout.write(self.style.SUCCESS("Seeding completed."))