from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/v1/users/register/'
        self.login_url = '/api/v1/users/login/'
        self.profile_url = '/api/v1/users/profile/'

    def test_register(self):
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)

    def test_register_password_mismatch(self):
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'StrongPass123!',
            'password_confirm': 'DifferentPass123!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        User.objects.create_user(email='dup@example.com', username='dup', password='pass123!')
        data = {
            'email': 'dup@example.com',
            'username': 'dup2',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login(self):
        User.objects.create_user(email='login@example.com', username='login', password='pass123!')
        data = {'email': 'login@example.com', 'password': 'pass123!'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)

    def test_login_invalid(self):
        data = {'email': 'wrong@example.com', 'password': 'wrongpass'}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile(self):
        user = User.objects.create_user(email='prof@example.com', username='prof', password='pass123!')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'prof@example.com')

    def test_profile_update(self):
        user = User.objects.create_user(email='upd@example.com', username='upd', password='pass123!')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.patch(self.profile_url, {'phone': '+111222333'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_profile_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
