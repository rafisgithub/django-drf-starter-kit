from django.urls import path
from .views import GoogleLoginAPIView

urlpatterns = [
    path('google-auth/', GoogleLoginAPIView.as_view(), name='google-auth'),
]
