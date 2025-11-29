from rest_framework import serializers
from apps.social_auth.utils import Google, register_with_google

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed



class GoogleSerializer(serializers.Serializer):
    
    access_token = serializers.CharField()

    def validate_access_token(self, access_token):
        user_data = Google.validate(access_token)
        try:
            user_data['sub']
        except KeyError:
            raise AuthenticationFailed('Invalid token')
        
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("Could not verify Google token")
        
        user_id = user_data['sub']
        email = user_data['email']
        first_name = user_data['given_name']
        last_name = user_data['family_name']
        provider = 'google'

        return register_with_google(provider, email, first_name, last_name)