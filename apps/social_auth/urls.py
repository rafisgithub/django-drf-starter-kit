from django.urls import path
from .views import GoogleAuthView

urlpatterns = [
    path('google-auth/', GoogleAuthView.as_view(), name='google-auth'),
]
