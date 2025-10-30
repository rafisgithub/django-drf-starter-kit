import email

from apps.user.managers import UserManager
from apps.user.models import User
from rest_framework import  serializers
from rest_framework_simplejwt.tokens import RefreshToken


class SocialAuthSignInSerializer(serializers.Serializer):

    email = serializers.EmailField()
    refresh_token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        user = User.objects.filter(email=attrs['email']).first()
        if not user:
           raise serializers.ValidationError({'email': 'User with this email does not exist.'})
        self.user = user
        return attrs

    def to_representation(self, instance):
        user = self.user
        refresh = RefreshToken.for_user(user)
        return {
            'id': user.id,
            'email': user.email,
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }
