import email

from apps.user.managers import UserManager
from .models import User, UserProfile, OTP
from rest_framework import  serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.utils.timezone import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .utils import generate_otp, send_normal_mail
from django.utils import timezone
from apps.utils.helpers import error


class SignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'User with this email already exists.'})
        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email')
        password = validated_data.pop('password')

        
        user = User.objects.create_user(email=email, password=password, **validated_data)

        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
        )

        return user
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.profile.first_name,
            'last_name': instance.profile.last_name,
            'email': instance.email,
        }


class CustomRefreshToken(RefreshToken):
    def __init__(self, user=None):
        super().__init__()
        if user:
            self.add_claims(user)

    def add_claims(self, user):
        self['id'] = user.id
        self['email'] = user.email
        self['avatar'] = user.avatar.url if user.avatar else None

class SignInSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    refresh_token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        user = User.objects.filter(email=attrs['email']).first()
        if not user:
           raise serializers.ValidationError({'email': 'User with this email does not exist.'})
        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Invalid password.'})
        self.user = user
        return attrs
    

    def to_representation(self, instance):

        user = self.user

        print(user)

        refresh = CustomRefreshToken(user=user)
        print("Refresh ", refresh)
        print("Access ", refresh.access_token)

        return {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token)
        }


class SignOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh_token')
        return attrs
    
    def save(self, **kwargs):
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
        except Exception as e:
            return ValidationError({'error': str(e)})

class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.CharField()
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        email = attrs.get('email')
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        user = User.objects.filter(email=email).first()
        if not user:
            raise ValidationError({'error': 'User not found.'})
        
        if not user.check_password(old_password):
            raise ValidationError({'error': 'Old password is incorrect.'})
        
        if new_password != confirm_password:
            raise ValidationError({'error': 'New password and confirm password is not match.'})
        
        if old_password == new_password:
            raise ValidationError({'error': 'The new password is not the same as the old password.'})
        
        try:
            validate_password(new_password)
        except Exception as e:
            raise ValidationError({'error': str(e.messages)})
        
        self.user = user
        return attrs
    
    def save(self):
        new_password = self.validated_data['new_password']
        user = self.user
        user.set_password(new_password)
        user.save()
        return user

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'User not found.'})

        otp_code = generate_otp()
        otp_hashed = make_password(otp_code)
        purpose = attrs['purpose']

        expires_at = timezone.now() + timedelta(minutes=3)

        OTP.objects.update_or_create(user=user, defaults={'otp': otp_hashed, 'is_verify': False, 'purpose': purpose, 'created_at': timezone.now(), 'expires_at': expires_at})

        data = {
            'subject': 'OTP for reset password.',
            'body': f'Your OTP is {otp_code}. Expire in 3 minutes.',
            'from': settings.EMAIL_HOST_USER,
            'to': [user.email,]
        }
        send_normal_mail(data)
        return attrs

class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        purpose = attrs.get('purpose')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise serializers.ValidationError({'error': 'User not found.'})

        try:
            otp_obj = OTP.objects.select_related('user').get(user=user, purpose=purpose)
            if otp_obj.is_verify:
                raise serializers.ValidationError({'error': 'OTP already used.'})
            if not otp_obj.is_expired():
                raise serializers.ValidationError({'error': 'OTP still valid. Please wait for it to expire.'})
        except OTP.DoesNotExist:
            raise serializers.ValidationError({'error': 'User with OTP not found.'})

        otp_code = generate_otp()
        otp_hashed = make_password(otp_code)
        purpose = attrs['purpose']

        expires_at = timezone.now() + timedelta(minutes=3)

        OTP.objects.update_or_create(user=user, defaults={'otp': otp_hashed, 'is_verify': False, 'purpose': purpose, 'created_at': timezone.now(), 'expires_at': expires_at})

        data = {
            'subject': 'OTP for reset password.',
            'body': f'Your OTP is {otp_code}. Expire in 3 minutes.',
            'from': settings.EMAIL_HOST_USER,
            'to': [user.email,]
        }
        send_normal_mail(data)
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        otp_input = data.get("otp")
        purpose = data.get("purpose")
        print(email, otp_input, purpose)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': "Invalid email."})

        try:
            otp_obj = OTP.objects.get(user=user, purpose=purpose)
        except OTP.DoesNotExist:
            raise serializers.ValidationError({'error': "OTP not found. Please request a new one."})

        if otp_obj.is_verify:
            raise serializers.ValidationError({'error': "OTP already varified."})

        if otp_obj.is_expired():
            otp_obj.delete()
            raise serializers.ValidationError({'error': "OTP expired. Please request a new one."})

        if not otp_obj.check_otp(otp_input):
            otp_obj.attempts += 1
            if otp_obj.attempts >= 3:
                otp_obj.delete()
                raise serializers.ValidationError({'error': "Too many incorrect attempts. Please request a new one."})
            otp_obj.save()
            raise serializers.ValidationError({'error': f"Incorrect OTP. Attempt {otp_obj.attempts}/3."})

        self.user = user
        self.otp_obj = otp_obj
        return data

    def save(self):
        self.otp_obj.is_verify = True
        self.otp_obj.attempts = 0
        self.otp_obj.save()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        purpose = data['purpose']
        new_password = data['new_password']
        confirm_password = data['confirm_password']

        try:
            user = User.objects.get(email=email)
            otp_obj = OTP.objects.get(user=user, purpose=purpose)
        except (User.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError({'error': "Invalid credentials or OTP."})

        if otp_obj.is_expired():
            otp_obj.delete()
            raise serializers.ValidationError({'error': "OTP has expired."})

        if not otp_obj.check_otp(otp):
            raise serializers.ValidationError({'error': "Incorrect OTP."})
        
        if not otp_obj.is_verify:
            raise serializers.ValidationError({'error': 'OTP not verified yet. Please verify OTP first.'})

        if new_password != confirm_password:
            raise serializers.ValidationError({'error': "Passwords do not match."})

        try:
            validate_password(new_password, user)
            print("Password validation passed")
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'error': str(e.messages)})

        data['user'] = user
        print(data)
        print(data['user'])
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        OTP.objects.filter(user=user, purpose=self.validated_data['purpose']).delete()


class UpdataProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar']
        extra_kwargs = {
            'avatar': { 'write_only': True },
        }




#  user
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "profile",
        ]


# UserProfile
class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "first_name",
            "last_name",
            "phone",
            "accepted_terms",
            "avatar",
            "dob",
            "created_at",
            "updated_at",
        ]

