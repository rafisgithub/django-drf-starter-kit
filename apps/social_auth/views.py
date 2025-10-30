from rest_framework.views import APIView
from social_django.utils import psa
from apps.social_auth.serializers import SocialAuthSignInSerializer
from apps.utils.helpers import success 
from rest_framework.validators import ValidationError


class SocialAuthGoogle(APIView):

    @psa('social:complete')

    def get(self, request, *args, **kwargs):

        serializer = SocialAuthSignInSerializer(data=request.data)

        if serializer.is_valid():

            return success(data=serializer.data, message="Signin successful.")
        
        raise ValidationError(serializer.errors)
