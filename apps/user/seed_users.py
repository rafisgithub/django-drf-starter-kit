from apps.user.models import User, UserProfile



def seed_users():
    user_data = [
        {
            "email": "rafi.cse.ahmed@gmail.com",
            "full_name": "Rafi Ahmed",
            "avatar": "avatars/1.jpg",
            "password": "12345678",
            "is_staff": True,
            "is_superuser": True,
            "term_and_condition_accepted": True,
          
        },
        {
            "email": "admin@admin.com",
            "full_name": "Admin User",
            "avatar": "avatars/1.jpg",
            "password": "12345678",
            "is_staff": True,
            "is_superuser": True,
            "term_and_condition_accepted": True,
          
        },

        {
            "email": "customer@customer.com",
            "full_name": "Customer User",
            "role": "customer",
            "avatar": "avatars/2.jpg",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "is_vendor": False,
            "term_and_condition_accepted": True,
           
        },
        {
            "email": "agency@agency.com",
            "full_name": "Agency User",
            "role": "agency",
            "avatar": "avatars/3.jpg",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "is_customer": True,
            "term_and_condition_accepted": True,
            
        },
        {
            "email": "customer1@customer.com",
            "full_name": "User Three",
            "avatar": "avatars/4.jpg",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "term_and_condition_accepted": True,
           
        },
        {
            "email": "customer2@customer.com",
            "full_name": "User Four",
            "avatar": "avatars/5.jpg",
            "password": "12345678",
            "is_staff": False,
            "is_superuser": False,
            "term_and_condition_accepted": True,
           
        }

    ]

    for user in user_data:
         User.objects.create_user(
            email=user["email"],
            full_name=user["full_name"],
            avatar=user["avatar"],
            password=user["password"],
            is_staff=user["is_staff"],
            is_superuser=user["is_superuser"],
            term_and_condition_accepted=user["term_and_condition_accepted"],
        )
         
         UserProfile.objects.create(
            user=User.objects.get(email=user["email"])
            )


    print("✅ User data seeded successfully.")
