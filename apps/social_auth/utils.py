from google.auth.transport import requests
from google.oauth2 import id_token
from apps.user.models import User, UserProfile
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class Google():
    @staticmethod
    def validate(access_token):  
        try:
            id_info = id_token.verify_oauth2_token(
                access_token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer')
            return id_info
        except ValueError as e:
            print(f"Token verification failed: {e}")
            raise AuthenticationFailed("Token is invalid")


def register_with_google(email, first_name, last_name):

    old_user = User.objects.filter(email=email)

    if old_user.exists():
        register_user = authenticate(email=email, password=settings.GOOGLE_SECRET_KEY)
        tokens = register_user.tokens()
        return {
            'email': register_user.email,
            'refresh_token': str(tokens.get('refresh')),
            'access_token': str(tokens.get('access')),
        }
        
       
    else:
        new_user = {
            'email': email,
            'password': settings.GOOGLE_SECRET_KEY
        }
        user = User.objects.create_user(**new_user)

        user.is_verified = True
        user.save()


        new_profile = {
            'user': user,
            'first_name': first_name,
            'last_name': last_name
        }

        UserProfile.objects.create(**new_profile)

        login_user = authenticate(email=email, password=settings.GOOGLE_SECRET_KEY)

        tokens = login_user.tokens()

        return {
            'email': login_user.email,
            'refresh_token': str(tokens.get('refresh')),
            'access_token': str(tokens.get('access')),
        }