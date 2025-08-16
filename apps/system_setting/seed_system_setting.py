from apps.system_setting.models import AboutSystem, SMTPSetting, SocialMedia

def seed_about_system():

    about_system = {
        "name": "Enter you application name",
        "title": "Your Title",
        "email": "your_email@example.com",
        "copyright": "© 2023 Enter you application name",
        "logo": "about_system/logo/1.png",
        "favicon": "about_system/favicon/1.png",
        "description": "Your description here.",
    }

    AboutSystem.objects.get_or_create(defaults=about_system)
    print("✅ About System seeded successfully.")


def seed_social_media():
    social_media = [
        {"name": "Facebook", "url": "https://facebook.com", "icon": "about_system/social_media/facebook.png"},
        {"name": "Twitter", "url": "https://twitter.com", "icon": "about_system/social_media/twitter.png"},
        {"name": "Instagram", "url": "https://instagram.com", "icon": "about_system/social_media/instagram.png"},
        {"name": "LinkedIn", "url": "https://linkedin.com", "icon": "about_system/social_media/linkedin.png"},
    ]

    for sm in social_media:
        SocialMedia.objects.get_or_create(**sm)

    print("✅ Social Media seeded successfully.")


def seed_smtp_credentials():
    smtp_credentials = {
        "host": "smtp.example.com",
        "port": 587,
        "username": "your_email@example.com",
        "password": "your_password",
        "encryption": "tls",
        "sender_name": "Your Name",
        "sender_email": "your_email@example.com",
        "is_active": True,
    }

    SMTPSetting.objects.get_or_create(defaults=smtp_credentials)
    print("✅ SMTP Credentials seeded successfully.")