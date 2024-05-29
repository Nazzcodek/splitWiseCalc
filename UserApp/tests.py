from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework import status





from django.contrib.auth import get_user_model

User = get_user_model()


# Create your tests here.

class CreateUserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_user_valid_data(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = self.client.post('/api/create_user/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_missing_fields(self):
        data = {
            'username': 'testuser',
            # Missing email and password
        }
        response = self.client.post('/api/create_user/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)






class LoginUserViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a user
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_login_valid_credentials(self):
            data = {
                'username': 'testuser',
                'password': 'testpassword'
            }
            
            response = self.client.post('/api/login_user/', data, format='json')
            print(response)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('token', response.data)  # Verify that the response contains a 'token' key
            self.assertTrue(response.data['token'])  # Verify that the token is not empty
            
        
    def test_login_invalid_credentials(self):
            data = {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
            response = self.client.post('/api/login_user/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

