# HTTP-Only Cookie Authentication Guide

## Overview

This authentication system uses JWT (JSON Web Tokens) stored in HTTP-only cookies to provide secure authentication for the API. This approach protects against XSS (Cross-Site Scripting) attacks by preventing JavaScript from accessing the authentication tokens.

## Why HTTP-Only Cookies?

### Security Benefits

1. **XSS Protection**: HTTP-only cookies cannot be accessed by JavaScript, preventing token theft via XSS attacks
2. **CSRF Protection**: SameSite cookie attribute prevents CSRF attacks
3. **Automatic Management**: Browsers handle cookie storage and transmission automatically
4. **Secure Transmission**: Secure flag ensures cookies are only sent over HTTPS in production

### Comparison with localStorage

| Feature | HTTP-Only Cookies | localStorage |
|---------|------------------|--------------|
| XSS Protection | ✅ Yes | ❌ No |
| CSRF Protection | ✅ Yes (with SameSite) | ✅ Yes (manual CSRF token) |
| Automatic handling | ✅ Yes | ❌ No |
| Cross-domain | ⚠️ Limited | ⚠️ Limited |
| Storage size | ~4KB | ~5-10MB |

## Architecture

### Token Types

1. **Access Token**
   - Lifetime: 15 minutes
   - Cookie name: `access_token`
   - Used for: API authentication
   - Storage: HTTP-only cookie

2. **Refresh Token**
   - Lifetime: 7 days
   - Cookie name: `refresh_token`
   - Used for: Obtaining new access tokens
   - Storage: HTTP-only cookie

### Authentication Flow

```
┌─────────┐                 ┌─────────┐
│ Client  │                 │ Server  │
└────┬────┘                 └────┬────┘
     │                           │
     │  POST /api/login/         │
     │  {email, password}        │
     │──────────────────────────>│
     │                           │
     │  200 OK                   │
     │  Set-Cookie: access_token │
     │  Set-Cookie: refresh_token│
     │<──────────────────────────│
     │                           │
     │  GET /api/me/             │
     │  Cookie: access_token     │
     │──────────────────────────>│
     │                           │
     │  200 OK                   │
     │  {user data}              │
     │<──────────────────────────│
     │                           │
     │  (15 min later)           │
     │  POST /api/refresh/       │
     │  Cookie: refresh_token    │
     │──────────────────────────>│
     │                           │
     │  200 OK                   │
     │  Set-Cookie: access_token │
     │  Set-Cookie: refresh_token│
     │<──────────────────────────│
     │                           │
     │  POST /api/logout/        │
     │  Cookie: access_token     │
     │──────────────────────────>│
     │                           │
     │  200 OK                   │
     │  Set-Cookie: (cleared)    │
     │<──────────────────────────│
```

## API Endpoints

### POST /api/login/

Authenticate user and receive tokens in cookies.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "client_admin",
    "clientId": 1,
    "clientName": "Acme Corp"
  }
}
```

**Cookies Set:**
- `access_token`: JWT access token (HttpOnly, SameSite=Lax, 15 min)
- `refresh_token`: JWT refresh token (HttpOnly, SameSite=Lax, 7 days)

### GET /api/me/

Get current authenticated user information.

**Authentication:** Required (access token in cookie or Authorization header)

**Response:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "client_admin",
    "clientId": 1,
    "clientName": "Acme Corp"
  }
}
```

### POST /api/refresh/

Refresh access token using refresh token.

**Authentication:** Requires refresh token in cookie

**Response:**
```json
{
  "message": "Token refreshed successfully"
}
```

**Cookies Updated:**
- `access_token`: New JWT access token
- `refresh_token`: New JWT refresh token (if rotation enabled)

### POST /api/logout/

Logout user and clear cookies.

**Authentication:** Required

**Response:**
```json
{
  "message": "Logout successful"
}
```

**Cookies Cleared:**
- `access_token`: Deleted (Max-Age=0)
- `refresh_token`: Deleted (Max-Age=0)

## Client Integration

### Web Browser (JavaScript/Frontend)

#### Basic Implementation

```javascript
// auth.js - Authentication utilities
class AuthService {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Login user with email and password
   * Cookies are automatically stored by the browser
   */
  async login(email, password) {
    const response = await fetch(`${this.baseUrl}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include' // Critical: allows cookies to be sent/received
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }
    
    const data = await response.json();
    return data.user;
  }

  /**
   * Get current user information
   * Cookies are sent automatically
   */
  async getCurrentUser() {
    const response = await fetch(`${this.baseUrl}/api/me/`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Not authenticated');
      }
      throw new Error('Failed to get user info');
    }
    
    const data = await response.json();
    return data.user;
  }

  /**
   * Refresh access token
   * Should be called when receiving 401 errors
   */
  async refreshToken() {
    const response = await fetch(`${this.baseUrl}/api/refresh/`, {
      method: 'POST',
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }
    
    return response.json();
  }

  /**
   * Logout user
   * Clears authentication cookies
   */
  async logout() {
    const response = await fetch(`${this.baseUrl}/api/logout/`, {
      method: 'POST',
      credentials: 'include'
    });
    
    return response.ok;
  }

  /**
   * Make authenticated API request with automatic token refresh
   */
  async authenticatedFetch(url, options = {}) {
    // Ensure credentials are included
    options.credentials = 'include';
    
    let response = await fetch(url, options);
    
    // If we get 401, try to refresh token and retry
    if (response.status === 401) {
      try {
        await this.refreshToken();
        // Retry the original request
        response = await fetch(url, options);
      } catch (error) {
        // Refresh failed, user needs to login again
        throw new Error('Authentication required');
      }
    }
    
    return response;
  }
}

// Export singleton
export const authService = new AuthService();
```

#### React Integration Example

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from './auth';

// Create authentication context
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const userData = await authService.login(email, password);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook for using auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

// Usage in components
function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      await login(email, password);
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}

function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <p>Role: {user?.role}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

#### Vue.js Integration Example

```javascript
// auth.js - Composable for Vue 3
import { ref, computed } from 'vue';
import { authService } from './authService';

const user = ref(null);
const loading = ref(true);

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value);

  const checkAuth = async () => {
    try {
      user.value = await authService.getCurrentUser();
    } catch (error) {
      user.value = null;
    } finally {
      loading.value = false;
    }
  };

  const login = async (email, password) => {
    const userData = await authService.login(email, password);
    user.value = userData;
    return userData;
  };

  const logout = async () => {
    await authService.logout();
    user.value = null;
  };

  return {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    checkAuth
  };
}
```

### Python (requests library)

#### Complete Python Client

```python
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class APIClient:
    """
    Python client for API with HTTP-only cookie authentication.
    Automatically handles token refresh and session management.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_refresh = None
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login and store cookies in session.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User data dictionary
            
        Raises:
            requests.HTTPError: If login fails
        """
        response = self.session.post(
            f"{self.base_url}/api/login/",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        print(f"✓ Logged in as: {data['user']['name']} ({data['user']['role']})")
        return data['user']
    
    def logout(self) -> bool:
        """
        Logout and clear cookies.
        
        Returns:
            True if logout successful
        """
        response = self.session.post(f"{self.base_url}/api/logout/")
        if response.status_code == 200:
            print("✓ Logged out successfully")
            return True
        return False
    
    def refresh_token(self) -> Dict[str, Any]:
        """
        Refresh the access token.
        
        Returns:
            Response message
            
        Raises:
            requests.HTTPError: If refresh fails
        """
        response = self.session.post(f"{self.base_url}/api/refresh/")
        response.raise_for_status()
        self.last_refresh = datetime.now()
        print("✓ Token refreshed")
        return response.json()
    
    def get_current_user(self) -> Dict[str, Any]:
        """
        Get current user information.
        Automatically refreshes token if expired.
        
        Returns:
            User data dictionary
        """
        response = self.session.get(f"{self.base_url}/api/me/")
        
        # If unauthorized, try refreshing token
        if response.status_code == 401:
            self.refresh_token()
            response = self.session.get(f"{self.base_url}/api/me/")
        
        response.raise_for_status()
        return response.json()['user']
    
    def should_refresh_token(self) -> bool:
        """
        Check if token should be refreshed (every 10 minutes).
        
        Returns:
            True if token should be refreshed
        """
        if not self.last_refresh:
            return False
        return datetime.now() - self.last_refresh > timedelta(minutes=10)
    
    def authenticated_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> requests.Response:
        """
        Make authenticated request with automatic token refresh.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        # Refresh token if needed
        if self.should_refresh_token():
            try:
                self.refresh_token()
            except requests.HTTPError:
                pass  # Continue with current token
        
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        
        # If unauthorized, try refreshing and retry once
        if response.status_code == 401:
            try:
                self.refresh_token()
                response = self.session.request(method, url, **kwargs)
            except requests.HTTPError:
                pass  # Return the 401 response
        
        return response


# Usage example
if __name__ == "__main__":
    # Create client
    client = APIClient()
    
    # Login
    try:
        user = client.login("user@example.com", "password123")
        print(f"User ID: {user['id']}")
        print(f"Client: {user.get('clientName', 'N/A')}")
    except requests.HTTPError as e:
        print(f"✗ Login failed: {e}")
        exit(1)
    
    # Get current user info
    try:
        user_info = client.get_current_user()
        print(f"\nCurrent user: {user_info}")
    except requests.HTTPError as e:
        print(f"✗ Failed to get user: {e}")
    
    # Make authenticated request
    response = client.authenticated_request('GET', '/predictions/predictions/')
    if response.ok:
        predictions = response.json()
        print(f"\n✓ Found {len(predictions)} predictions")
    
    # Logout
    client.logout()
```

### cURL Examples

#### Complete Testing Script

```bash
#!/bin/bash
# test_api.sh - Complete API testing with HTTP-only cookies

set -e  # Exit on error

BASE_URL="http://localhost:8000"
COOKIES_FILE="cookies.txt"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}==================================${NC}"
echo -e "${YELLOW}API Testing with HTTP-Only Cookies${NC}"
echo -e "${YELLOW}==================================${NC}\n"

# Test 1: Login
echo -e "${YELLOW}[1/9] Testing Login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Login successful${NC}"
  echo "$BODY" | python3 -m json.tool
else
  echo -e "${RED}✗ Login failed (HTTP $HTTP_CODE)${NC}"
  echo "$BODY"
  exit 1
fi

# Test 2: Get current user
echo -e "\n${YELLOW}[2/9] Testing Get Current User...${NC}"
USER_RESPONSE=$(curl -s "$BASE_URL/api/me/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$USER_RESPONSE" | tail -n1)
BODY=$(echo "$USER_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Got current user${NC}"
  echo "$BODY" | python3 -m json.tool
else
  echo -e "${RED}✗ Failed to get user (HTTP $HTTP_CODE)${NC}"
fi

# Test 3: Get upcoming matches (public endpoint)
echo -e "\n${YELLOW}[3/9] Testing Get Upcoming Matches...${NC}"
MATCHES_RESPONSE=$(curl -s "$BASE_URL/leagues/upcoming-matches/" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$MATCHES_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Got upcoming matches${NC}"
  MATCH_COUNT=$(echo "$MATCHES_RESPONSE" | sed '$d' | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
  echo "Found $MATCH_COUNT upcoming matches"
else
  echo -e "${RED}✗ Failed to get matches (HTTP $HTTP_CODE)${NC}"
fi

# Test 4: Get standings (public endpoint)
echo -e "\n${YELLOW}[4/9] Testing Get League Standings...${NC}"
STANDINGS_RESPONSE=$(curl -s "$BASE_URL/leagues/standings/" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$STANDINGS_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Got league standings${NC}"
else
  echo -e "${RED}✗ Failed to get standings (HTTP $HTTP_CODE)${NC}"
fi

# Test 5: Get predictions (requires auth)
echo -e "\n${YELLOW}[5/9] Testing Get Predictions...${NC}"
PRED_RESPONSE=$(curl -s "$BASE_URL/predictions/predictions/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$PRED_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Got predictions${NC}"
  PRED_COUNT=$(echo "$PRED_RESPONSE" | sed '$d' | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
  echo "Found $PRED_COUNT predictions"
else
  echo -e "${RED}✗ Failed to get predictions (HTTP $HTTP_CODE)${NC}"
fi

# Test 6: Get client rankings (requires auth)
echo -e "\n${YELLOW}[6/9] Testing Get Client Rankings...${NC}"
RANK_RESPONSE=$(curl -s "$BASE_URL/predictions/client-rankings/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$RANK_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Got client rankings${NC}"
else
  echo -e "${RED}✗ Failed to get rankings (HTTP $HTTP_CODE)${NC}"
fi

# Test 7: Refresh token
echo -e "\n${YELLOW}[7/9] Testing Token Refresh...${NC}"
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/refresh/" \
  -b "$COOKIES_FILE" \
  -c "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$REFRESH_RESPONSE" | tail -n1)
BODY=$(echo "$REFRESH_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Token refreshed successfully${NC}"
  echo "$BODY" | python3 -m json.tool
else
  echo -e "${RED}✗ Failed to refresh token (HTTP $HTTP_CODE)${NC}"
fi

# Test 8: Verify refreshed token works
echo -e "\n${YELLOW}[8/9] Testing With Refreshed Token...${NC}"
USER_RESPONSE=$(curl -s "$BASE_URL/api/me/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$USER_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Refreshed token works${NC}"
else
  echo -e "${RED}✗ Refreshed token failed (HTTP $HTTP_CODE)${NC}"
fi

# Test 9: Logout
echo -e "\n${YELLOW}[9/9] Testing Logout...${NC}"
LOGOUT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/logout/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$LOGOUT_RESPONSE" | tail -n1)
BODY=$(echo "$LOGOUT_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}✓ Logout successful${NC}"
  echo "$BODY" | python3 -m json.tool
else
  echo -e "${RED}✗ Logout failed (HTTP $HTTP_CODE)${NC}"
fi

# Test 10: Verify logout (should fail)
echo -e "\n${YELLOW}[Bonus] Testing Access After Logout...${NC}"
USER_RESPONSE=$(curl -s "$BASE_URL/api/me/" \
  -b "$COOKIES_FILE" \
  -w "\n%{http_code}")

HTTP_CODE=$(echo "$USER_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" == "401" ]; then
  echo -e "${GREEN}✓ Access denied after logout (as expected)${NC}"
else
  echo -e "${RED}✗ Unexpected response: HTTP $HTTP_CODE${NC}"
fi

# Cleanup
rm -f "$COOKIES_FILE"

echo -e "\n${YELLOW}==================================${NC}"
echo -e "${GREEN}✓ All tests completed!${NC}"
echo -e "${YELLOW}==================================${NC}"
```

Make the script executable:
```bash
chmod +x test_api.sh
./test_api.sh
```

## Security Considerations

### Protection Mechanisms

1. **XSS Protection**
   - HTTP-only flag prevents JavaScript access
   - Tokens cannot be stolen via XSS attacks

2. **CSRF Protection**
   - SameSite=Lax prevents cross-site requests
   - Cookies only sent with same-site requests

3. **Token Expiration**
   - Access tokens expire in 15 minutes
   - Limits exposure window if token is compromised

4. **Token Rotation**
   - Refresh tokens are rotated on use
   - Prevents token reuse attacks

5. **Secure Transmission**
   - Secure flag requires HTTPS in production
   - Prevents man-in-the-middle attacks

### Best Practices

1. **Always use HTTPS in production**
   - Set `AUTH_COOKIE_SECURE = True`
   - Ensures encrypted transmission

2. **Implement rate limiting**
   - Prevent brute force attacks
   - Limit login attempts per IP

3. **Monitor authentication events**
   - Log all login/logout events
   - Detect suspicious activity

4. **Handle token refresh proactively**
   - Refresh tokens before expiration
   - Provide seamless user experience

5. **Validate all inputs**
   - Server-side validation
   - Prevent injection attacks

## Configuration

### Django Settings

```python
# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# Cookie Settings
AUTH_COOKIE = 'access_token'
AUTH_COOKIE_REFRESH = 'refresh_token'
AUTH_COOKIE_SECURE = not DEBUG  # True in production
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_SAMESITE = 'Lax'
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_MAX_AGE = 60 * 15  # 15 minutes
AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 * 24 * 7  # 7 days
```

### Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set `AUTH_COOKIE_SECURE = True`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring
- [ ] Regular security audits

## Troubleshooting

### Common Issues

#### 1. Cookies Not Being Set

**Symptoms:**
- Login succeeds but subsequent requests are unauthorized
- Browser doesn't show cookies in DevTools

**Solutions:**
- Ensure `credentials: 'include'` in all fetch requests
- Check that the API domain matches the frontend domain (or configure CORS properly)
- Verify the server's cookie path is `/` (not a subdirectory)
- In development, if using different ports (frontend on :3000, backend on :8000), configure CORS:
  ```python
  # settings.py
  CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
  CORS_ALLOW_CREDENTIALS = True
  ```

**Debug Steps:**
```javascript
// Check if cookies are being set
fetch('/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
  credentials: 'include'
})
.then(response => {
  console.log('Set-Cookie headers:', response.headers.get('Set-Cookie'));
  // Note: Set-Cookie headers might not be visible in browser due to security
  // Check browser DevTools > Application > Cookies instead
});
```

#### 2. 401 Unauthorized Errors

**Symptoms:**
- Authenticated requests return 401
- User was logged in but now gets unauthorized

**Solutions:**
- Access token expired (15 minutes) - call `/api/refresh/` endpoint
- Refresh token expired (7 days) - user must login again
- Implement automatic token refresh in your client:

```javascript
async function fetchWithAuth(url, options = {}) {
  options.credentials = 'include';
  let response = await fetch(url, options);
  
  if (response.status === 401) {
    // Try refreshing token
    const refreshResponse = await fetch('/api/refresh/', {
      method: 'POST',
      credentials: 'include'
    });
    
    if (refreshResponse.ok) {
      // Retry original request
      response = await fetch(url, options);
    } else {
      // Refresh failed - redirect to login
      window.location.href = '/login';
    }
  }
  
  return response;
}
```

#### 3. CORS Errors

**Symptoms:**
- Browser console shows CORS policy errors
- Preflight OPTIONS requests fail

**Solutions:**
- Install and configure django-cors-headers:
  ```bash
  pip install django-cors-headers
  ```
  
  ```python
  # settings.py
  INSTALLED_APPS = [
      ...
      'corsheaders',
  ]
  
  MIDDLEWARE = [
      'corsheaders.middleware.CorsMiddleware',
      'django.middleware.common.CommonMiddleware',
      ...
  ]
  
  # Allow your frontend origin
  CORS_ALLOWED_ORIGINS = [
      "http://localhost:3000",
      "http://127.0.0.1:3000",
  ]
  
  # Required for cookies
  CORS_ALLOW_CREDENTIALS = True
  ```

#### 4. Cookies Cleared on Page Reload

**Symptoms:**
- Cookies disappear after page refresh
- User logged out unexpectedly

**Solutions:**
- Check browser settings - ensure third-party cookies aren't blocked
- Verify cookie max-age is set correctly on the server
- In development with HTTP (not HTTPS), some browsers may clear cookies
- For Chrome/Firefox: Check DevTools > Application > Cookies to see cookie details

#### 5. Cross-Domain Authentication Issues

**Symptoms:**
- Authentication works on same domain but fails cross-domain
- Cookies not sent with cross-origin requests

**Solutions:**
- HTTP-only cookies work best with same-domain requests
- For cross-domain, consider these options:
  1. Use a reverse proxy to serve frontend and backend on same domain
  2. Use subdomains (api.example.com and app.example.com)
  3. Use Authorization header with Bearer token instead of cookies:
  
```javascript
// Store token in memory (not localStorage for security)
let accessToken = null;

async function login(email, password) {
  const response = await fetch('/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include'
  });
  
  const data = await response.json();
  // For cross-domain, extract token from response if available
  // and use Authorization header instead of cookies
  return data;
}

async function fetchWithAuthHeader(url, options = {}) {
  if (accessToken) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${accessToken}`
    };
  }
  return fetch(url, options);
}
```

#### 6. Token Refresh Loop

**Symptoms:**
- Continuous refresh requests
- App becomes unresponsive

**Solutions:**
- Add refresh debouncing:

```javascript
let refreshPromise = null;

async function refreshToken() {
  // Prevent multiple simultaneous refresh requests
  if (refreshPromise) {
    return refreshPromise;
  }
  
  refreshPromise = fetch('/api/refresh/', {
    method: 'POST',
    credentials: 'include'
  }).finally(() => {
    refreshPromise = null;
  });
  
  return refreshPromise;
}
```

#### 7. Testing Authentication in Development

**Issue:** Hard to test authentication flow during development

**Solutions:**

1. **Use cURL for quick tests:**
```bash
# Save cookies to file
curl -c cookies.txt -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123"}'

# Use cookies for authenticated request
curl -b cookies.txt http://localhost:8000/api/me/
```

2. **Create test users:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from users.models import ClientM, ClientUserM

# Create a client
client = ClientM.objects.create(
    name="Test Corp",
    admin_name="Test Admin",
    admin_email="admin@test.com"
)

# Create a user
user = User.objects.create_user(
    username="testuser",
    email="test@example.com",
    password="testpass123"
)

# Link user to client
ClientUserM.objects.create(
    user=user,
    role=ClientUserM.CLIENT_ADMIN,
    client=client
)
```

3. **Use Browser DevTools:**
   - Open DevTools (F12)
   - Go to Application > Cookies
   - Verify `access_token` and `refresh_token` cookies are present
   - Check cookie properties (HttpOnly, Secure, SameSite)

#### 8. Production Issues

**Issue:** Authentication works in development but fails in production

**Checklist:**
- [ ] HTTPS is enabled (`AUTH_COOKIE_SECURE = True`)
- [ ] Domain is correctly configured
- [ ] CORS origins include production frontend URL
- [ ] Cookie SameSite attribute is appropriate for your setup
- [ ] SECRET_KEY is strong and secret
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS includes your domain

## Testing

### Running the Test Suite

```bash
# Run all tests
python manage.py test

# Run authentication tests only
python manage.py test users.test_authentication -v 2

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage

The authentication system includes comprehensive tests:

- ✅ Login with valid credentials
- ✅ Login with invalid credentials
- ✅ Token refresh flow
- ✅ Logout and cookie clearing
- ✅ Cookie-based authentication
- ✅ Authorization header authentication
- ✅ Authenticated endpoint access
- ✅ Role-based user data (client_admin, client_user, root_admin)
- ✅ Cookie properties (HttpOnly, SameSite, Secure)

### Manual Testing

#### Using the Example Client

Run the provided example client:

```bash
python example_client.py
```

Expected output:
```
============================================================
HTTP-Only Cookie Authentication Example
============================================================

1. Logging in...
✓ Login successful
  User: John Doe
  Role: client_admin
  Cookies: ['access_token', 'refresh_token']

2. Getting user info...
✓ Got user info
  {
    "id": 1,
    "name": "John Doe",
    "email": "test@example.com",
    "role": "client_admin",
    "clientId": 1,
    "clientName": "Test Corp"
  }

3. Refreshing token...
✓ Token refreshed successfully
  New cookies: ['access_token', 'refresh_token']

3b. Verifying refreshed token...
✓ Got user info
  {...}

4. Logging out...
✓ Logout successful
  Cookies cleared

5. Attempting to access after logout...
✓ Access denied after logout (as expected)

============================================================
Example completed!
============================================================
```

#### Using Browser DevTools

1. **Open your browser's DevTools** (F12)
2. **Navigate to Application > Cookies**
3. **Login** to your application
4. **Verify cookies:**
   - `access_token` should be present
   - `refresh_token` should be present
   - Both should have `HttpOnly` flag ✓
   - Both should have `SameSite=Lax` ✓
   - In production, both should have `Secure` flag ✓

5. **Test token expiration:**
   - Wait 15 minutes (or change token lifetime in settings for testing)
   - Make an authenticated request
   - Should receive 401 Unauthorized
   - Call `/api/refresh/` to get new token
   - Retry the request - should succeed

6. **Test logout:**
   - Click logout
   - Check cookies - both should be removed
   - Try accessing protected endpoint - should fail with 401

### Integration Testing

Create automated integration tests:

```python
# tests/test_integration.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from users.models import ClientM, ClientUserM

class AuthenticationIntegrationTest(TestCase):
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        
        # Create test client organization
        self.org_client = ClientM.objects.create(
            name="Test Corp",
            admin_name="Test Admin",
            admin_email="admin@test.com"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        
        # Link user to client
        ClientUserM.objects.create(
            user=self.user,
            role=ClientUserM.CLIENT_ADMIN,
            client=self.org_client
        )
    
    def test_complete_authentication_flow(self):
        """Test complete authentication flow from login to logout."""
        
        # 1. Login
        response = self.client.post('/api/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)
        
        # Verify cookie properties
        access_cookie = response.cookies['access_token']
        self.assertTrue(access_cookie['httponly'])
        self.assertEqual(access_cookie['samesite'], 'Lax')
        
        # 2. Access protected endpoint
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['user']['email'], 'test@example.com')
        
        # 3. Access user's predictions
        response = self.client.get('/predictions/predictions/')
        self.assertEqual(response.status_code, 200)
        
        # 4. Refresh token
        response = self.client.post('/api/refresh/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.cookies)
        
        # 5. Logout
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, 200)
        
        # 6. Try accessing after logout (should fail)
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, 401)
```

Run integration tests:
```bash
python manage.py test tests.test_integration
```

## Performance Considerations

### Token Refresh Strategy

**Option 1: Proactive Refresh (Recommended)**
Refresh token before it expires to avoid interruptions:

```javascript
// Refresh token every 10 minutes (access token expires in 15)
setInterval(async () => {
  try {
    await authService.refreshToken();
    console.log('Token refreshed proactively');
  } catch (error) {
    console.error('Failed to refresh token:', error);
  }
}, 10 * 60 * 1000); // 10 minutes
```

**Option 2: Reactive Refresh**
Refresh only when receiving 401 errors:

```javascript
// Handled in authenticatedFetch method (see Client Integration section)
```

### Caching User Info

Cache user information to reduce API calls:

```javascript
class UserCache {
  constructor() {
    this.user = null;
    this.lastFetch = null;
    this.cacheTime = 5 * 60 * 1000; // 5 minutes
  }
  
  async getUser(forceRefresh = false) {
    const now = Date.now();
    
    if (!forceRefresh && this.user && 
        this.lastFetch && (now - this.lastFetch < this.cacheTime)) {
      return this.user; // Return cached user
    }
    
    // Fetch fresh user data
    const response = await fetch('/api/me/', { credentials: 'include' });
    this.user = await response.json();
    this.lastFetch = now;
    
    return this.user;
  }
  
  clear() {
    this.user = null;
    this.lastFetch = null;
  }
}
```

## Support and Resources

### Documentation
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API endpoint reference
- [README.md](README.md) - Project overview and setup instructions

### Example Code
- `example_client.py` - Python example demonstrating authentication flow

### Getting Help

If you encounter issues:

1. **Check this guide** for troubleshooting common problems
2. **Review test suite** to see working examples
3. **Run example client** to verify server is working correctly
4. **Check server logs** for detailed error messages:
   ```bash
   python manage.py runserver
   # Watch console output for errors
   ```

5. **Verify environment:**
   ```bash
   # Check installed packages
   pip list | grep -E "django|rest"
   
   # Run migrations
   python manage.py migrate
   
   # Run tests
   python manage.py test users.test_authentication -v 2
   ```

### Quick Reference

**Login:**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' \
  -c cookies.txt
```

**Authenticated Request:**
```bash
curl http://localhost:8000/api/me/ -b cookies.txt
```

**Refresh Token:**
```bash
curl -X POST http://localhost:8000/api/refresh/ \
  -b cookies.txt -c cookies.txt
```

**Logout:**
```bash
curl -X POST http://localhost:8000/api/logout/ -b cookies.txt
```
