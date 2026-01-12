from apps.system_setting.models import AboutSystem, SMTPSetting, SocialMedia, SystemColor

def seed_system_setting():

    system_setting = {
        "name": "Enter you application name",
        "title": "Your Title",
        "email": "your_email@example.com",
        "copyright": "© 2023 Enter you application name",
        "logo": "system_setting/logo/1.png",
        "favicon": "system_setting/favicon/1.png",
        "description": "Your description here.",
    }

    AboutSystem.objects.get_or_create(defaults=system_setting)
    print("✅ About System seeded successfully.")


def seed_social_media():
    social_media = [
        {"name": "Facebook", "url": "https://facebook.com", "icon": "system_setting/social_media/facebook.png"},
        {"name": "Twitter", "url": "https://twitter.com", "icon": "system_setting/social_media/twitter.png"},
        {"name": "Instagram", "url": "https://instagram.com", "icon": "system_setting/social_media/instagram.png"},
        {"name": "LinkedIn", "url": "https://linkedin.com", "icon": "system_setting/social_media/linkedin.png"},
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


def seed_system_color():
    SystemColor.objects.get_or_create({
        "name" : "orange",
        "code" : "#FFA500"
    })
    print("✅ System Color seeded successfully.")