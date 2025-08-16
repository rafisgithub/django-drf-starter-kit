from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

def update_profile(request):
    try:
        profile_pk = request.user.profile.pk 
        profile_link = reverse_lazy("admin:users_userprofile_change", args=[profile_pk])
    except Exception:
        profile_link = reverse_lazy("admin:users_userprofile_changelist")  # fallback

    return profile_link
