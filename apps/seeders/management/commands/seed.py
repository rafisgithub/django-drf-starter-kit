from django.core.management.base import BaseCommand

from apps.system_setting.seed_system_setting import seed_about_system, seed_social_media, seed_smtp_credentials
from apps.users.seed_users import seed_users
from apps.products.seed_products import seed_categories, seed_subcategories, seed_sizes, seed_colors, seed_products
from apps.cms.seed_cms import seed_faq_types, seed_faqs


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        seed_users()
        seed_categories()
        seed_subcategories()
        seed_sizes()
        seed_colors()
        seed_products()
        seed_about_system()
        seed_social_media()
        seed_smtp_credentials()
        seed_faq_types()
        seed_faqs()

        self.stdout.write(self.style.SUCCESS("Seeding completed."))