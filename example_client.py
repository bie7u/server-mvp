#!/usr/bin/env python3
"""
Example client script demonstrating HTTP-only cookie authentication.

This script shows how to:
1. Login and receive cookies
2. Make authenticated requests
3. Refresh tokens
4. Logout

Usage:
    python example_client.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def login(email, password):
    """Login and get cookies."""
    print("\n1. Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Login successful")
        print(f"  User: {data['user']['name']}")
        print(f"  Role: {data['user']['role']}")
        print(f"  Cookies: {list(response.cookies.keys())}")
        return response.cookies
    else:
        print(f"✗ Login failed: {response.json()}")
        return None


def get_user_info(cookies):
    """Get current user info using cookies."""
    print("\n2. Getting user info...")
    response = requests.get(
        f"{BASE_URL}/api/me/",
        cookies=cookies
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Got user info")
        print(f"  {json.dumps(data['user'], indent=2)}")
        return data
    else:
        print(f"✗ Failed to get user info: {response.status_code}")
        return None


def refresh_token(cookies):
    """Refresh the access token."""
    print("\n3. Refreshing token...")
    response = requests.post(
        f"{BASE_URL}/api/refresh/",
        cookies=cookies
    )
    
    if response.status_code == 200:
        print(f"✓ Token refreshed successfully")
        print(f"  New cookies: {list(response.cookies.keys())}")
        # Merge new cookies with existing ones
        cookies.update(response.cookies)
        return cookies
    else:
        print(f"✗ Failed to refresh token: {response.status_code}")
        return cookies


def logout(cookies):
    """Logout and clear cookies."""
    print("\n4. Logging out...")
    response = requests.post(
        f"{BASE_URL}/api/logout/",
        cookies=cookies
    )
    
    if response.status_code == 200:
        print(f"✓ Logout successful")
        print(f"  Cookies cleared")
        return True
    else:
        print(f"✗ Logout failed: {response.status_code}")
        return False


def main():
    """Run the example flow."""
    print("=" * 60)
    print("HTTP-Only Cookie Authentication Example")
    print("=" * 60)
    
    # Login
    cookies = login("test@example.com", "testpass123")
    if not cookies:
        print("\n✗ Cannot continue without valid login")
        return
    
    # Get user info
    get_user_info(cookies)
    
    # Refresh token
    cookies = refresh_token(cookies)
    
    # Get user info again to verify new token works
    print("\n3b. Verifying refreshed token...")
    get_user_info(cookies)
    
    # Logout
    logout(cookies)
    
    # Try to access after logout (should fail)
    print("\n5. Attempting to access after logout...")
    response = requests.get(f"{BASE_URL}/api/me/", cookies=cookies)
    if response.status_code == 401:
        print("✓ Access denied after logout (as expected)")
    else:
        print(f"✗ Unexpected response: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to server")
        print("  Make sure the Django server is running:")
        print("  python manage.py runserver")
    except Exception as e:
        print(f"\n✗ Error: {e}")
