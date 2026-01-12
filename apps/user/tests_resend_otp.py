from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.user.models import User, OTP
from apps.system_setting.models import AboutSystem
from django.utils import timezone
from datetime import timedelta

class ResendOTPViewTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        
        # Ensure AboutSystem exists for email template
        AboutSystem.objects.create(
            name="Test System",
            title="Test Title",
            email="test@system.com",
            copyright="Test Copyright",
            description="Test Description"
        )
        
        self.resend_otp_url = reverse('resend-otp')

    def test_resend_otp_success_empty_otp(self):
        """
        Verify that ResendOTP works even if no OTP object exists for the user.
        """
        # Ensure no OTP exists initially
        OTP.objects.filter(user=self.user).delete()
        
        data = {
            "email": self.email,
            "purpose": "activation"
        }
        
        response = self.client.post(self.resend_otp_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that an OTP was created
        self.assertTrue(OTP.objects.filter(user=self.user, purpose="activation").exists())
