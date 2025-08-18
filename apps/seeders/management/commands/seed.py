from django.core.management.base import BaseCommand

from apps.cms.seed_data import seed_faq, seed_page
from apps.system_setting.seed_data import seed_system_color, seed_system_setting, seed_social_media, seed_smtp_credentials
from apps.users.seed_users import seed_users


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        seed_users()
        seed_system_setting()
        seed_social_media()
        seed_smtp_credentials()
        seed_system_color()
        seed_page()
        seed_faq()

        self.stdout.write(self.style.SUCCESS("Seeding completed."))