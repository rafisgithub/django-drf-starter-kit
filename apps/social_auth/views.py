from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.utils import psa
from apps.users.serializers import SignInSerializer
from apps.utils.helpers import success , error
from rest_framework.validators import ValidationError


class SocialAuthGoogle(APIView):
    @psa('social:complete')
    def get(self, request, *args, **kwargs):        
        serializer = SignInSerializer(data=request.data)
        if serializer.is_valid():
            return success(data=serializer.data, message="Signin successful.")
        raise ValidationError(serializer.errors)
