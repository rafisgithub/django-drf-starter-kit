from apps.users.models import User, UserProfile


def seed_users():
    user_data = [
        {
            "email": "rafi.cse.ahmed@gmail.com",
            "password": "12345678",
            "is_staff": True,
            "is_superuser": True,
            "userprofile": {
                "first_name": "Super",
                "last_name": "Ahmed",
                "phone": "+1234567890",
                "accepted_terms": True,
                "avatar": "avatars/1.jpg",
                "dob": "1990-01-01",
            },
        },
        {
            "email": "admin@admin.com",
            "password": "12345678",
            "is_staff": True,
            "is_superuser": True,
            "userprofile": {
                "first_name": "Admin",
                "last_name": "User",
                "phone": "+1234567890",
                "accepted_terms": True,
                "avatar": "avatars/1.jpg",
                "dob": "1990-01-01",
            },
        },

        {
            "email": "user1@user1.com",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "is_vendor": False,
            "userprofile": {
                "first_name": "User",
                "last_name": "User",
                "phone": "+12345678",
                "accepted_terms": True,
                "avatar": "avatars/2.jpg",
                "dob": "1990-01-01",
            },
        },
        {
            "email": "user2@user2.com",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "is_customer": True,
            "userprofile": {
                "first_name": "User",
                "last_name": "User",
                "phone": "+12345678",
                "accepted_terms": True,
                "avatar": "avatars/3.jpg",
                "dob": "1990-01-01",
            },
        },
        {
            "email": "user3@user3.com",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "userprofile": {
                "first_name": "User3",
                "last_name": "User",
                "phone": "+12345678",
                "accepted_terms": True,
                "avatar": "avatars/3.jpg",
                "dob": "1990-01-01",
            },
        },
        {
            "email": "user4@user4.com",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "userprofile": {
                "first_name": "User4",
                "last_name": "User",
                "phone": "+12345678",
                "accepted_terms": True,
                "avatar": "avatars/4.jpg",
                "dob": "1990-01-01",
            },
        }

    ]

    for user in user_data:
        user_instance = User.objects.create_user(
            email=user["email"],
            password=user["password"],
            is_staff=user["is_staff"],
            is_superuser=user["is_superuser"],
        )

        UserProfile.objects.get_or_create(
            user=user_instance,
            first_name=user["userprofile"]["first_name"],
            last_name=user["userprofile"]["last_name"],
            phone=user["userprofile"]["phone"],
            accepted_terms=user["userprofile"]["accepted_terms"],
            avatar=user["userprofile"]["avatar"],
            dob=user["userprofile"]["dob"],
        )


    print("✅ User data seeded successfully.")