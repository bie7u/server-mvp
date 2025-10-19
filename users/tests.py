from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import ClientM, ClientUserM


class AuthenticationTests(TestCase):
    """Test suite for HTTP-only cookie authentication."""

    def setUp(self):
        """Set up test client and test users."""
        self.client = APIClient()
        
        # Create a test client organization
        self.test_client = ClientM.objects.create(
            name='Test Corp',
            admin_name='Admin User',
            admin_email='admin@testcorp.com',
            status='active'
        )
        
        # Create a root admin user
        self.root_admin = User.objects.create_user(
            username='rootadmin',
            email='root@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        ClientUserM.objects.create(
            user=self.root_admin,
            role=ClientUserM.CLIENT_ADMIN,
            is_root_client_admin=True
        )
        
        # Create a client admin user
        self.client_admin = User.objects.create_user(
            username='clientadmin',
            email='admin@testcorp.com',
            password='testpass123'
        )
        ClientUserM.objects.create(
            user=self.client_admin,
            role=ClientUserM.CLIENT_ADMIN,
            client=self.test_client
        )
        
        # Create a client user
        self.client_user = User.objects.create_user(
            username='clientuser',
            email='user@testcorp.com',
            password='testpass123'
        )
        ClientUserM.objects.create(
            user=self.client_user,
            role=ClientUserM.CLIENT_USER,
            client=self.test_client
        )
        
        # URLs
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.current_user_url = reverse('current-user')

    def test_login_success_root_admin(self):
        """Test successful login for root admin user."""
        response = self.client.post(self.login_url, {
            'email': 'root@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'root@example.com')
        self.assertEqual(response.data['user']['role'], 'root_admin')
        self.assertIsNone(response.data['user']['clientId'])
        
        # Check that session cookie is set
        self.assertIn('sessionid', response.cookies)
        # Verify HTTP-only flag
        session_cookie = response.cookies['sessionid']
        self.assertTrue(session_cookie['httponly'])

    def test_login_success_client_admin(self):
        """Test successful login for client admin user."""
        response = self.client.post(self.login_url, {
            'email': 'admin@testcorp.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'admin@testcorp.com')
        self.assertEqual(response.data['user']['role'], 'client_admin')
        self.assertEqual(response.data['user']['clientId'], self.test_client.id)
        self.assertEqual(response.data['user']['clientName'], 'Test Corp')

    def test_login_success_client_user(self):
        """Test successful login for client user."""
        response = self.client.post(self.login_url, {
            'email': 'user@testcorp.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'user@testcorp.com')
        self.assertEqual(response.data['user']['role'], 'client_user')
        self.assertEqual(response.data['user']['clientId'], self.test_client.id)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(self.login_url, {
            'email': 'root@example.com',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid credentials')

    def test_login_nonexistent_email(self):
        """Test login with non-existent email."""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_email(self):
        """Test login with missing email."""
        response = self.client.post(self.login_url, {
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """Test login with missing password."""
        response = self.client.post(self.login_url, {
            'email': 'root@example.com'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Test login with inactive user account."""
        # Create inactive user
        inactive_user = User.objects.create_user(
            username='inactive',
            email='inactive@example.com',
            password='testpass123',
            is_active=False
        )
        
        response = self.client.post(self.login_url, {
            'email': 'inactive@example.com',
            'password': 'testpass123'
        })
        
        # Inactive user should return 401 as it's an authentication failure
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_authenticated(self):
        """Test getting current user when authenticated."""
        # Login first
        self.client.post(self.login_url, {
            'email': 'root@example.com',
            'password': 'testpass123'
        })
        
        # Get current user
        response = self.client.get(self.current_user_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'root@example.com')

    def test_current_user_unauthenticated(self):
        """Test getting current user when not authenticated."""
        response = self.client.get(self.current_user_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_success(self):
        """Test successful logout."""
        # Login first
        self.client.post(self.login_url, {
            'email': 'root@example.com',
            'password': 'testpass123'
        })
        
        # Logout
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logged out successfully')
        
        # Verify session is cleared - try accessing protected endpoint
        response = self.client.get(self.current_user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_unauthenticated(self):
        """Test logout when not authenticated."""
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_session_persistence(self):
        """Test that session persists across requests."""
        # Login
        self.client.post(self.login_url, {
            'email': 'root@example.com',
            'password': 'testpass123'
        })
        
        # Make multiple requests - should stay authenticated
        for _ in range(3):
            response = self.client.get(self.current_user_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['user']['email'], 'root@example.com')


class UserSerializerTests(TestCase):
    """Test suite for UserSerializer."""

    def setUp(self):
        """Set up test users."""
        self.test_client = ClientM.objects.create(
            name='Test Corp',
            admin_name='Admin User',
            admin_email='admin@testcorp.com',
            status='active'
        )
        
        self.root_admin = User.objects.create_user(
            username='rootadmin',
            email='root@example.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        ClientUserM.objects.create(
            user=self.root_admin,
            role=ClientUserM.CLIENT_ADMIN,
            is_root_client_admin=True
        )

    def test_serializer_root_admin_role(self):
        """Test that root admin role is correctly serialized."""
        from users.serializers import UserSerializer
        
        serializer = UserSerializer(self.root_admin)
        self.assertEqual(serializer.data['role'], 'root_admin')

    def test_serializer_includes_all_fields(self):
        """Test that serializer includes all required fields."""
        from users.serializers import UserSerializer
        
        serializer = UserSerializer(self.root_admin)
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'clientId', 'clientName']
        
        for field in expected_fields:
            self.assertIn(field, serializer.data)
