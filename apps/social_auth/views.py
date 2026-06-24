import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from apps.user.models import User, UserProfile
from apps.utils.helpers import error
from uuid import uuid4
import secrets

from apps.user.serializers import CustomRefreshToken
from apps.user.utils import get_user_agent_hash, create_hybrid_auth_response

GOOGLE_TOKENINFO_URL = "https://www.googleapis.com/oauth2/v3/tokeninfo"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
GOOGLE_REQUEST_TIMEOUT = 10  # seconds
AVATAR_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return error("Access token is required", status_code=status.HTTP_400_BAD_REQUEST)

        # 1. Validate the token's audience. Google's userinfo endpoint accepts ANY
        # valid Google access token regardless of which OAuth client minted it, so
        # without this check an attacker could log in using a token issued to a
        # different app (token substitution / confused-deputy account takeover).
        try:
            tokeninfo_response = requests.get(
                GOOGLE_TOKENINFO_URL,
                params={'access_token': access_token},
                timeout=GOOGLE_REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            return error("Could not reach Google to validate token", status_code=status.HTTP_502_BAD_GATEWAY)

        if tokeninfo_response.status_code != 200:
            return error("Invalid or expired access token", status_code=status.HTTP_401_UNAUTHORIZED)

        tokeninfo = tokeninfo_response.json()
        if tokeninfo.get('aud') != settings.GOOGLE_CLIENT_ID:
            return error("Access token was not issued for this application", status_code=status.HTTP_401_UNAUTHORIZED)

        # 2. Fetch profile details.
        try:
            userinfo_response = requests.get(
                GOOGLE_USERINFO_URL,
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=GOOGLE_REQUEST_TIMEOUT,
            )
        except requests.RequestException:
            return error("Could not reach Google to fetch user info", status_code=status.HTTP_502_BAD_GATEWAY)

        if userinfo_response.status_code != 200:
            return error("Failed to fetch user info from Google", status_code=status.HTTP_400_BAD_REQUEST)

        user_info = userinfo_response.json()
        email = user_info.get('email')
        name = user_info.get('name')
        given_name = user_info.get('given_name')
        family_name = user_info.get('family_name')
        picture = user_info.get('picture')

        if not email:
            return error("Email not available in Google user info", status_code=status.HTTP_400_BAD_REQUEST)

        # 3. Only trust verified emails. An unverified email could otherwise be used
        # to take over an existing local account that shares the same address.
        email_verified = user_info.get('email_verified')
        if email_verified in (False, 'false'):
            return error("Google email is not verified", status_code=status.HTTP_400_BAD_REQUEST)

        # 4. Create or fetch the user atomically to avoid a race between two
        # concurrent logins (email is unique) and to avoid orphan users.
        full_name = name or " ".join(filter(None, [given_name, family_name])) or None
        with transaction.atomic():
            user, created = User.objects.get_or_create(
                email=User.objects.normalize_email(email),
                defaults={'full_name': full_name},
            )
            if created:
                # Social-auth users authenticate via Google, not a local password.
                user.set_password(secrets.token_urlsafe(32))
                user.save(update_fields=['password'])
                self._save_avatar(user, picture)
                UserProfile.objects.create(user=user)

        # Bind tokens to the requesting user agent (existing security feature).
        user_agent_hash = get_user_agent_hash(request)
        refresh = CustomRefreshToken.for_user(user, user_agent_hash=user_agent_hash)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

        user_data = {
            'id': user.id,
            'email': user.email,
            'role': user.role,
        }

        return create_hybrid_auth_response(
            data=user_data,
            tokens=tokens,
            request=request,
            message="Google login successful.",
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    def _save_avatar(user, picture_url):
        """Best-effort download of the Google profile picture. Failures are
        non-fatal — the account is still created without an avatar."""
        if not picture_url:
            return
        try:
            image_response = requests.get(picture_url, timeout=GOOGLE_REQUEST_TIMEOUT, stream=True)
        except requests.RequestException:
            return
        if image_response.status_code != 200:
            return
        content = image_response.content
        if not content or len(content) > AVATAR_MAX_BYTES:
            return
        user.avatar.save(f"profile_{uuid4().hex}.jpg", ContentFile(content), save=True)
