import requests
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from apps.user.models import User, UserProfile
from apps.utils.helpers import error
from uuid import uuid4
import secrets

from apps.user.serializers import CustomRefreshToken
from apps.user.utils import get_user_agent_hash, create_hybrid_auth_response

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return error("Access token is required", status_code=status.HTTP_400_BAD_REQUEST)

        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        response = requests.get(
            user_info_url,
            headers={'Authorization': f'Bearer {access_token}'}
        )

        if response.status_code != 200:
            return error("Failed to fetch user info from Google", status_code=status.HTTP_400_BAD_REQUEST)

        user_info = response.json()
        email = user_info.get('email')
        name = user_info.get('name')
        given_name = user_info.get('given_name')  
        family_name = user_info.get('family_name')  
        picture = user_info.get('picture') 

        if not email:
            return error("Email not available in Google user info", status_code=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists, if not create one.
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Generate secure random password for social auth users
            random_password = secrets.token_urlsafe(32)
            user = User.objects.create_user(
                email=email,
                password=random_password
            )
            if picture:
                image_response = requests.get(picture)
                if image_response.status_code == 200:
                    file_name = f"profile_{uuid4().hex}.jpg"  
                    if hasattr(user, 'avatar'):
                        user.avatar.save(file_name, ContentFile(image_response.content))

            UserProfile.objects.create(
                user=user,
                first_name=given_name,
                last_name=family_name
            )
        
        # Get user agent hash for token binding (security feature)
        user_agent_hash = get_user_agent_hash(request)
        
        # Generate tokens with user agent binding
        refresh = CustomRefreshToken.for_user(user, user_agent_hash=user_agent_hash)
        
        # Prepare tokens
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        
        # User data to return
        user_data = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }
        
        # Create hybrid response (supports both web and mobile)
        response = create_hybrid_auth_response(
            data=user_data,
            tokens=tokens,
            request=request,
            message="Google login successful.",
            status_code=status.HTTP_200_OK
        )
        
        return response