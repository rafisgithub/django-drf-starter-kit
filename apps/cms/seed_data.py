from apps.cms.models import FAQ, Page

def seed_page():
    pages = [
    {
        "title": "Privacy Policy",
        "slug": "privacy-policy",
        "content": "This Privacy Policy explains how we collect, use, and protect your personal data when you use our website and services.",
        "type": "privacy_policy",
        "status": True
    },
    {
        "title": "Terms and Conditions",
        "slug": "terms-and-conditions",
        "content": "These Terms and Conditions govern your use of our website and services. By accessing the site, you agree to comply with these rules.",
        "type": "terms_and_conditions",
        "status": True
    },
    {
        "title": "Cookie Policy",
        "slug": "cookie-policy",
        "content": "Our website uses cookies to enhance user experience. This policy explains what cookies we use and how you can manage them.",
        "type": "cookie_policy",
        "status": True
    },
    {
        "title": "Imprint",
        "slug": "imprint",
        "content": "This Imprint provides legal information about our company, including address, contact details, and responsible representatives.",
        "type": "imprint",
        "status": True
    }
]
    for page in pages:
        Page.objects.create(**page)
    print("✅ Pages seeded successfully.")


def seed_faq():
    faqs = [
        {
            "question": "How can I create an account?",
            "answer": "You can create an account by clicking the 'Sign Up' button and filling out the registration form.",
            "status": True
        },
        {
            "question": "How do I reset my password?",
            "answer": "Click on 'Forgot Password' on the login page, then follow the instructions to reset your password.",
            "status": True
        },
        {
            "question": "Can I change my email address?",
            "answer": "Yes, you can update your email in your profile settings under 'Account Information'.",
            "status": True
        },
        {
            "question": "How do I contact support?",
            "answer": "You can reach our support team via the 'Contact Us' page or by emailing support@example.com.",
            "status": True
        },
        {
            "question": "Is my personal information safe?",
            "answer": "Yes, we use industry-standard security measures to protect your data.",
            "status": True
        }
    ]

    for faq in faqs:
        FAQ.objects.create(**faq)

    print("✅ FAQs seeded successfully.")