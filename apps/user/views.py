from .models import User, UserProfile
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .authentication import CookieJWTAuthentication
from rest_framework.validators import ValidationError
from .utils import clear_auth_cookies


# Use hybrid response utility
from .utils import create_hybrid_auth_response

from .serializers import (
    SignUpSerializer,
    SignInSerializer,
    SignOutSerializer,
    ChangePasswordSerializer,
    SendOTPSerializer,
    ResendOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UpdataProfileAvatarSerializer,
)

from apps.utils.helpers import success, error


# Create your views here.
class SignUpView(APIView):
    permission_classes = []

    def post(self, request):

        serializer = SignUpSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()

            return success(data=[],message="Signup successful. Please verify your email using the OTP sent.", status_code=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)

class SignInView(APIView):

    permission_classes = []

    def post(self, request):
        print("REQUEST DATA:", request.data)
        
        serializer = SignInSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.data
            
            
            tokens = {
                'access': result['access'],
                'refresh': result['refresh']
            }
            
            response = create_hybrid_auth_response(
                data=result['user'],
                tokens=tokens,
                request=request,
                message="Signin successful.",
                status_code=status.HTTP_200_OK
            )
            
            return response
        raise ValidationError(serializer.errors)


class SignOutView(APIView):
  
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        # Get tokens from request body or cookies
        data = request.data.copy()
        if 'refresh_token' not in data and 'refresh_token' in request.COOKIES:
            data['refresh_token'] = request.COOKIES['refresh_token']
        if 'access_token' not in data and 'access_token' in request.COOKIES:
            data['access_token'] = request.COOKIES['access_token']
        
        print("COOKIES:", request.COOKIES)
        
        serializer = SignOutSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            # Create response
            response = success(data=[], message="Logout successful.", status_code=status.HTTP_200_OK)
            
            # Clear cookies for web clients
            is_web = getattr(request, 'is_web_client', True)
            if is_web or 'access_token' in request.COOKIES:
                clear_auth_cookies(response)
            
            return response
        return error(message="Logout failed.", status_code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)



class ChangePasswordView(APIView):
    
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return success(data=[], message="Password change successfully.", status_code=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=[], message="OTP send to mail successfully.", status_code=status.HTTP_200_OK)
        errors = serializer.errors
        if "email" in errors:
            errors["error"] = errors.pop("email")
        raise ValidationError(errors)

class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=[], message="OTP send to mail successfully.", status_code=status.HTTP_200_OK)
        errors = serializer.errors
        if "email" in errors:
            errors["error"] = errors.pop("email")
        raise ValidationError(errors)

class VerifyOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            result = serializer.data


            purpose = request.data.get('purpose')
            
            if purpose == 'create_account':


                tokens = {
                    'access': result['access'],
                    'refresh': result['refresh']
                }
                
                response = create_hybrid_auth_response(
                    data=result['user'],
                    tokens=tokens,
                    request=request,
                    message="OTP verified successfully.",
                    status_code=status.HTTP_200_OK
                )
            
                return response
            else:
                return success(data=[], message="OTP verified successfully.", status_code=status.HTTP_200_OK)
        return error(message="OTP verify is failed.", status_code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success(data=[], message="Password reset successfully.", status_code=status.HTTP_200_OK)
        errors = serializer.errors
        if "non_field_errors" in errors:
            errors["error"] = errors.pop("non_field_errors")
        return error(message="Password reset failed.", status_code=status.HTTP_400_BAD_REQUEST, errors=errors)



class UpdataProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        user = request.user
        
        serializer = UpdataProfileAvatarSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success(data=serializer.data, message="Profile avatar update successfully.", status_code=status.HTTP_200_OK)
        return error(message="Profile avatar update failed.", status_code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def put(self, request):
        user = request.user

        try:
            user = User.objects.get(id=user.id)
            name = request.data.get('full_name', '')
            user.full_name = name
            user.save()
            return success(data={'full_name': user.full_name}, message="Profile update successfully.", status_code=status.HTTP_200_OK)
        except User.DoesNotExist:
            return error(message="Profile update failed.", status_code=status.HTTP_400_BAD_REQUEST, errors={"error": "User does not exist."})


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        user = request.user

        try:
            profile = user.user_profile
        except UserProfile.DoesNotExist:
            return success(
                data={},
                message="Profile not found.",
                status_code=status.HTTP_200_OK
            )

        data = {
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': profile.phone,
            'dob': profile.dob,
        }
        return success(data=data, message="Profile get successfully.", status_code=status.HTTP_200_OK)


class CookieTokenRefreshView(TokenRefreshView):
    """
    Hybrid Token Refresh View
    
    Supports both Web and Mobile clients:
    - Web: Reads refresh token from HttpOnly cookie, returns new tokens in cookies
    - Mobile: Reads refresh token from request body, returns new tokens in response body
    """
    
    def post(self, request, *args, **kwargs):
        # Inject refresh token from cookie into data if not present (for web clients)
        data = request.data.copy()
        if 'refresh' not in data and 'refresh_token' in request.COOKIES:
            data['refresh'] = request.COOKIES['refresh_token']
        
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token_data = serializer.validated_data
        
        # Use hybrid response utility
        from .utils import create_hybrid_refresh_response
        
        tokens = {
            'access': token_data['access'],
            'refresh': token_data.get('refresh')  # May not exist if rotation is disabled
        }
        
        response = create_hybrid_refresh_response(
            tokens=tokens,
            request=request,
            message="Token refreshed successfully.",
            status_code=status.HTTP_200_OK
        )
        
        return response


class CookieTokenVerifyView(TokenVerifyView):
    """
    Hybrid Token Verify View
    
    Supports both Web and Mobile clients:
    - Web: Reads access token from HttpOnly cookie
    - Mobile: Reads token from request body
    """
    
    def post(self, request, *args, **kwargs):
        # Inject access token from cookie into data if not present (for web clients)
        data = request.data.copy()
        if 'token' not in data and 'access_token' in request.COOKIES:
            data['token'] = request.COOKIES['access_token']
        
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        return success(data=[], message="Token is valid.", status_code=status.HTTP_200_OK)




