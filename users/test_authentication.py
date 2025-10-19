"""
Tests for HTTP-only cookie JWT authentication.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import status
from users.models import ClientM, ClientUserM


User = get_user_model()


class AuthenticationTestCase(TestCase):
    """Test cases for cookie-based JWT authentication."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create client organization
        self.test_client = ClientM.objects.create(
            name='Test Client',
            admin_name='Admin User',
            admin_email='admin@testclient.com',
            status='active'
        )
        
        # Create client user profile
        self.client_user = ClientUserM.objects.create(
            user=self.user,
            role='client_admin',
            client=self.test_client
        )
        
    def test_login_success(self):
        """Test successful login with valid credentials."""
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['message'], 'Login successful')
        
        # Check user data in response
        user_data = response.json()['user']
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['role'], 'client_admin')
        self.assertEqual(user_data['clientId'], self.test_client.id)
        
        # Check cookies are set
        self.assertIn(settings.AUTH_COOKIE, response.cookies)
        self.assertIn(settings.AUTH_COOKIE_REFRESH, response.cookies)
        
        # Verify cookie properties
        access_cookie = response.cookies[settings.AUTH_COOKIE]
        self.assertTrue(access_cookie['httponly'])
        self.assertEqual(access_cookie['samesite'], 'Lax')
        self.assertEqual(access_cookie['path'], '/')
        
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['message'], 'Invalid credentials')
        
        # Check cookies are not set
        self.assertNotIn(settings.AUTH_COOKIE, response.cookies)
        
    def test_login_missing_fields(self):
        """Test login with missing required fields."""
        response = self.client.post('/api/login/', {
            'email': 'test@example.com'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post('/api/login/', {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_me_endpoint_authenticated(self):
        """Test /me endpoint with valid authentication."""
        # First login to get cookies
        login_response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        # Extract cookies
        access_token = login_response.cookies[settings.AUTH_COOKIE].value
        
        # Call /me endpoint with cookie
        self.client.cookies[settings.AUTH_COOKIE] = access_token
        response = self.client.get('/api/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.json()['user']
        self.assertEqual(user_data['email'], 'test@example.com')
        self.assertEqual(user_data['role'], 'client_admin')
        
    def test_me_endpoint_unauthenticated(self):
        """Test /me endpoint without authentication."""
        response = self.client.get('/api/me/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_logout(self):
        """Test logout clears cookies."""
        # First login
        login_response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        access_token = login_response.cookies[settings.AUTH_COOKIE].value
        
        # Logout
        self.client.cookies[settings.AUTH_COOKIE] = access_token
        logout_response = self.client.post('/api/logout/')
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertEqual(logout_response.json()['message'], 'Logout successful')
        
        # Check cookies are cleared (max_age=0 or expires in past)
        self.assertIn(settings.AUTH_COOKIE, logout_response.cookies)
        self.assertEqual(logout_response.cookies[settings.AUTH_COOKIE].value, '')
        
    def test_refresh_token(self):
        """Test token refresh with valid refresh token."""
        # First login
        login_response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        refresh_token = login_response.cookies[settings.AUTH_COOKIE_REFRESH].value
        
        # Refresh token
        self.client.cookies[settings.AUTH_COOKIE_REFRESH] = refresh_token
        refresh_response = self.client.post('/api/refresh/')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response.json()['message'], 'Token refreshed successfully')
        
        # Check new access token is set
        self.assertIn(settings.AUTH_COOKIE, refresh_response.cookies)
        
    def test_refresh_token_missing(self):
        """Test token refresh without refresh token."""
        response = self.client.post('/api/refresh/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['message'], 'Refresh token not found')
        
    def test_superuser_role(self):
        """Test superuser gets root_admin role."""
        # Create superuser
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        response = self.client.post('/api/login/', {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.json()['user']
        self.assertEqual(user_data['role'], 'root_admin')
        self.assertIsNone(user_data['clientId'])


class CookieJWTAuthenticationTestCase(TestCase):
    """Test cases for CookieJWTAuthentication class."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_authentication_with_cookie(self):
        """Test authentication using cookie."""
        # Login to get token
        login_response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        access_token = login_response.cookies[settings.AUTH_COOKIE].value
        
        # Make authenticated request using cookie
        self.client.cookies[settings.AUTH_COOKIE] = access_token
        response = self.client.get('/api/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_authentication_with_header(self):
        """Test authentication using Authorization header."""
        # Login to get token
        login_response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        access_token = login_response.cookies[settings.AUTH_COOKIE].value
        
        # Make authenticated request using header
        response = self.client.get(
            '/api/me/',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
