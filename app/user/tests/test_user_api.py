from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_test_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public - unauthenticated)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'user@test.com',
            'password': 'testpass',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)

        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        self.assertEqual(user.name, payload['name'])
        self.assertEqual(user.email, payload['email'])

    def test_user_exists(self):
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'user@test.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        create_test_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Tests that the password must be more than 8 characters"""
        payload = {
            'email': 'user@test.com',
            'password': 'pw',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Tests that a token is created for the user'''
        payload = {
            "email": "test@gmail.com",
            "password": "test123!"
        }

        create_test_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """"Tests that token is not created with the wrong credentials"""
        create_test_user(email="test@gmail.com", password="test123@")
        payload = {
            "email": "test@gmail.com",
            "password": "test123!"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_user_not_found(self):
        """"Tests that token is not created if user is not found"""
        payload = {
            "email": "test@gmail.com",
            "password": "test123!"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_missing_field(self):
        """"Tests that token is not created if user is not found"""
        create_test_user(email="test@gmail.com", password="test123@")
        payload = {
            "email": "test@gmail.com",
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)
