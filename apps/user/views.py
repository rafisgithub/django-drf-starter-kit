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
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'Logout successful.', 'data': serializer.data}, status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'success':False, 'message': 'Logout failed.', 'data': serializer.errors}, status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'Password change successfully.', 'data': []}, status.HTTP_200_OK)
        raise ValidationError(serializer.errors)

class SendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'OTP send to mail successfully.', 'data': []}, status.HTTP_200_OK)
        errors = serializer.errors
        if "email" in errors:
            errors["error"] = errors.pop("email")
        raise ValidationError(errors)

class ResendOTPView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'OTP send to mail successfully.', 'data': []}, status.HTTP_200_OK)
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
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'OTP verify is successfully.', 'data': []}, status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'success':False, 'message': 'OTP verify is failed.', 'data': serializer.errors}, status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'Password reset successfully.', 'data': []}, status.HTTP_200_OK)
        errors = serializer.errors
        if "non_field_errors" in errors:
            errors["error"] = errors.pop("non_field_errors")
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'success':False, 'message': 'Password reset failed.', 'data': errors}, status.HTTP_400_BAD_REQUEST)



class UpdataProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user

        try:
            userProfile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist as e:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': 'false', 'message': 'User not Found.', 'data': str(e)}, status.HTTP_400_BAD_REQUEST)

        serializer = UpdataProfileAvatarSerializer(userProfile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK, 'success':True, 'message': 'Profile avatar update successfully.', 'data': serializer.data}, status.HTTP_200_OK)
        return Response({'status':status.HTTP_400_BAD_REQUEST, 'success':False, 'message': 'Profile avatar update failed.', 'data': serializer.errors}, status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def put(self, request):
        user = request.user

        try:
            userProfile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'message': 'User not found.', 'data': []})

        serializer = UserProfileSerializer(userProfile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': status.HTTP_200_OK, 'success': True, 'message': 'Profile update successfully.', 'data': serializer.data})
        return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'message': 'Profile update failed.', 'data': serializer.errors})


class ProfileGet(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user

        try:
            profile = UserProfile.objects.select_related('user').get(user=user)
        except UserProfile.DoesNotExist:
            return Response({'status': status.HTTP_400_BAD_REQUEST, 'success': False, 'message': 'User not found.', 'data': []})

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
        return Response({'status': status.HTTP_200_OK, 'success': True, 'message': 'Profile get successfully.', 'data': data})




