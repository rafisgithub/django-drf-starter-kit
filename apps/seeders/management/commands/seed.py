from django.core.management.base import BaseCommand

from apps.system_setting.seed_system_setting import seed_about_system, seed_social_media, seed_smtp_credentials
from apps.users.seed_users import seed_users


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        seed_users()
        seed_about_system()
        seed_social_media()
        seed_smtp_credentials()
    

        self.stdout.write(self.style.SUCCESS("Seeding completed."))