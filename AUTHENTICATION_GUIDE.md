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

```javascript
// Login
async function login(email, password) {
  const response = await fetch('/api/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
    credentials: 'include' // Important: include cookies
  });
  
  const data = await response.json();
  return data.user;
}

// Make authenticated request
async function getUserInfo() {
  const response = await fetch('/api/me/', {
    credentials: 'include' // Important: include cookies
  });
  
  return response.json();
}

// Refresh token
async function refreshToken() {
  const response = await fetch('/api/refresh/', {
    method: 'POST',
    credentials: 'include'
  });
  
  return response.ok;
}

// Logout
async function logout() {
  const response = await fetch('/api/logout/', {
    method: 'POST',
    credentials: 'include'
  });
  
  return response.ok;
}
```

### Python (requests library)

```python
import requests

# Create session to persist cookies
session = requests.Session()

# Login
response = session.post('http://localhost:8000/api/login/', json={
    'email': 'user@example.com',
    'password': 'password123'
})
user = response.json()['user']

# Make authenticated request
response = session.get('http://localhost:8000/api/me/')
user_info = response.json()

# Refresh token
response = session.post('http://localhost:8000/api/refresh/')

# Logout
response = session.post('http://localhost:8000/api/logout/')
```

### cURL

```bash
# Login and save cookies
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt

# Make authenticated request
curl http://localhost:8000/api/me/ -b cookies.txt

# Refresh token
curl -X POST http://localhost:8000/api/refresh/ \
  -b cookies.txt \
  -c cookies.txt

# Logout
curl -X POST http://localhost:8000/api/logout/ -b cookies.txt
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

**Issue: Cookies not being set**
- Ensure `credentials: 'include'` in fetch requests
- Check that domain and path match
- Verify CORS configuration

**Issue: 401 Unauthorized errors**
- Check if access token expired
- Call `/api/refresh/` to get new token
- Verify cookies are being sent with request

**Issue: CSRF errors**
- Ensure SameSite attribute is set correctly
- Check that request origin matches cookie domain

**Issue: Cookies cleared on page reload**
- Verify max-age is set correctly
- Check browser settings for third-party cookies

## Testing

Run the test suite:

```bash
# All tests
python manage.py test

# Authentication tests only
python manage.py test users.test_authentication -v 2
```

Test coverage includes:
- ✅ Login with valid/invalid credentials
- ✅ Token refresh flow
- ✅ Logout and cookie clearing
- ✅ Cookie and header authentication
- ✅ Authenticated endpoint access
- ✅ Role-based user data

## Support

For issues or questions:
1. Check API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. Review example client: `example_client.py`
3. Run test suite to verify setup
