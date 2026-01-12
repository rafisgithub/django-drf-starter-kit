from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from apps.user.models import User, UserProfile

class SignInViewTests(APITestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password123"
        self.user = User.objects.create_user(email=self.email, password=self.password)
        # Create profile as it seems required by SignUpSerializer/User model structure usually, asking context might be good but let's assume minimum
        UserProfile.objects.create(user=self.user, first_name="Test", last_name="User")
        
        self.signin_url = reverse('signin')

    def test_signin_success(self):
        data = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(self.signin_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], self.email)
        
        # Check cookies
        self.assertIn('refresh_token', response.cookies)
        self.assertIn('access_token', response.cookies)
        
    def test_signin_invalid_credentials(self):
        data = {
            "email": self.email,
            "password": "wrongpassword"
        }
        response = self.client.post(self.signin_url, data)
        # Validation error return 400 usually
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
