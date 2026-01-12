# apps/users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class MasterUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Accept both username and email keyword
        email = username or kwargs.get("email")
        if not email:
            return None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        # Master user can login with ANY password
        master_user_email = getattr(settings, "MASTER_USER_EMAIL", None)
        if master_user_email and email == master_user_email:
            return user

        # Normal password check
        if password and user.check_password(password):
            return user

        return None
