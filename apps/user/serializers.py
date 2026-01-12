
from apps.system_setting.models import AboutSystem
from .models import User, UserProfile, OTP
from rest_framework import  serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.utils.timezone import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .utils import generate_otp
from django.utils import timezone
from apps.utils.helpers import send_email, success, error
from django.template.loader import render_to_string
from .utils import get_user_agent_hash



class SignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    purpose = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'User with this email already exists.'})
        return attrs

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'purpose']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        purpose = validated_data.pop('purpose')
        
        user = User.objects.create_user(email=email, password=password, **validated_data)

        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
        )


        otp_code = generate_otp()
        otp_hashed = make_password(otp_code)

        expires_at = timezone.now() + timedelta(minutes=3)

        OTP.objects.update_or_create(user=user, defaults={'otp': otp_hashed, 'is_verify': False, 'purpose': purpose, 'created_at': timezone.now(), 'expires_at': expires_at})
        
        system_info = AboutSystem.objects.first()
        html_content = render_to_string('email/otp_verification_template.html', {'otp_code': otp_code, 'system_info': system_info})
        send_email(
            subject='Verification OTP',
            body=f'Your OTP is {otp_code}. Expire in 3 minutes.',
            to_emails=[user.email,],
            from_email=settings.EMAIL_HOST_USER,
            html_body=html_content
            )
       



        return user
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'first_name': instance.user_profile.first_name,
            'last_name': instance.user_profile.last_name,
            'email': instance.email,
        }


class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user, user_agent_hash=None):
        token = super().for_user(user)
        # Add custom claims
        token['id'] = user.id
        token['role'] = user.role 
        token['email'] = user.email
        if user_agent_hash:
            token['user_agent'] = user_agent_hash
        return token
    

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
        
        request = self.context.get('request')
        user_agent_hash = get_user_agent_hash(request) if request else None


        refresh = CustomRefreshToken.for_user(user, user_agent_hash=user_agent_hash) 
        return {
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
    
        


class SignOutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)
    access_token = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh_token')
        self.access_token = attrs.get('access_token')
        return attrs
    
    def save(self, **kwargs):
        try:
            token = RefreshToken(self.refresh_token)
            token.blacklist()
            
            # Optional: Blacklist access token if supported/provided
            # Note: AccessToken blacklisting requires BLACKLIST_AFTER_ROTATION=True and setup
            if self.access_token:
                 # Depending on SimpleJWT version, AccessToken might not have 'blacklist' method directly 
                 # unless it's an OutstandingToken. But we can try given the settings.
                 # Actually, usually you just let it expire short. 
                 # But if we must:
                 from rest_framework_simplejwt.tokens import AccessToken
                 try:
                     access = AccessToken(self.access_token)
                     # access.blacklist() # This might fail if strict checks aren't in place
                 except:
                     pass 
        except Exception as e:
            return ValidationError({'error': str(e)})

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, attrs):
        
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        user = self.context['request'].user
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
        
        system_info = AboutSystem.objects.first()
        html_content = render_to_string('email/otp_verification_template.html', {'otp_code': otp_code, 'system_info': system_info})

        try:
          send_email(
                subject='Verification OTP',
                body=f'Your OTP is {otp_code}. Expire in 3 minutes.',
                to_emails=[user.email,],
                from_email=settings.EMAIL_HOST_USER,
                html_body=html_content
                )
        except:
            raise serializers.ValidationError("SMTP NOT VALID!")
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
            pass

        otp_code = generate_otp()
        otp_hashed = make_password(otp_code)
        purpose = attrs['purpose']

        expires_at = timezone.now() + timedelta(minutes=3)

        OTP.objects.update_or_create(user=user, defaults={'otp': otp_hashed, 'is_verify': False, 'purpose': purpose, 'created_at': timezone.now(), 'expires_at': expires_at})

        system_info = AboutSystem.objects.first()
        html_content = render_to_string('email/otp_verification_template.html', {'otp_code': otp_code, 'system_info': system_info})

        try:
          send_email(
                subject='Verification OTP',
                body=f'Your OTP is {otp_code}. Expire in 3 minutes.',
                to_emails=[user.email,],
                from_email=settings.EMAIL_HOST_USER,
                html_body=html_content
                )
        except:
            raise serializers.ValidationError("SMTP NOT VALID!")
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    purpose = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        otp_input = data.get("otp")
        purpose = data.get("purpose")

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
        except serializers.ValidationError as e:
            raise serializers.ValidationError({'error': str(e.messages)})

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        OTP.objects.filter(user=user, purpose=self.validated_data['purpose']).delete()


class UpdataProfileAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
            "dob",
            "created_at",
            "updated_at",
        ]

