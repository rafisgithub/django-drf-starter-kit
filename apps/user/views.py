from .models import User, UserProfile
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.urls import reverse_lazy
from django.db.models import Count
import json
from django.db.models.functions import TruncDate
from rest_framework.validators import ValidationError
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
    UserProfileSerializer,
)
from django.http import Http404
from apps.utils.helpers import success, error


# Create your views here.
class SignUpView(APIView):
    permission_classes = []

    def post(self, request):

        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success(data=serializer.data,message="User created successfully.",code=status.HTTP_201_CREATED)
        raise ValidationError(serializer.errors)

class SignInView(APIView):

    permission_classes = []

    def post(self, request):
        
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=serializer.data, message="Signin successful.", code=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = SignOutSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success(data=[], message="Logout successful.", code=status.HTTP_200_OK)
        return error(message="Logout failed.", code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success(data=[], message="Password change successfully.", code=status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=[], message="OTP send to mail successfully.", code=status.HTTP_200_OK)
        errors = serializer.errors
        if "email" in errors:
            errors["error"] = errors.pop("email")
        raise ValidationError(errors)

class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=[], message="OTP send to mail successfully.", code=status.HTTP_200_OK)
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
            return success(data=[], message="OTP verify is successfully.", code=status.HTTP_200_OK)
        return error(message="OTP verify is failed.", code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success(data=[], message="Password reset successfully.", code=status.HTTP_200_OK)
        errors = serializer.errors
        if "non_field_errors" in errors:
            errors["error"] = errors.pop("non_field_errors")
        return error(message="Password reset failed.", code=status.HTTP_400_BAD_REQUEST, errors=errors)



class UpdataProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user

        try:
            userProfile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist as e:
            return error(message="User not Found.", code=status.HTTP_400_BAD_REQUEST, errors=str(e))

        serializer = UpdataProfileAvatarSerializer(userProfile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success(data=serializer.data, message="Profile avatar update successfully.", code=status.HTTP_200_OK)
        return error(message="Profile avatar update failed.", code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user

        try:
            userProfile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist:
            return error(message="User not found.", code=status.HTTP_400_BAD_REQUEST, errors=[])

        serializer = UserProfileSerializer(userProfile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success(data=serializer.data, message="Profile update successfully.", code=status.HTTP_200_OK)
        return error(message="Profile update failed.", code=status.HTTP_400_BAD_REQUEST, errors=serializer.errors)


class ProfileGet(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        try:
            profile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist:
            return success(data=[], message="Profile not found.", code=status.HTTP_200_OK)

        data = {
            'id': profile.id,
            'email': profile.user.email,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone': profile.phone,
            'accepted_terms': profile.accepted_terms,
            'avatar_url': profile.avatar.url if profile.avatar else None,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
        }
        return success(data=data, message="Profile get successfully.", code=status.HTTP_200_OK)




