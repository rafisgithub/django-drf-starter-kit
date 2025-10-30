from django.urls import path
from .views import SocialAuthGoogle

urlpatterns = [
    path('google-auth/', SocialAuthGoogle.as_view(), name='google-auth'),
]
