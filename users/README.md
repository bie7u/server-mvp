# Users App - Authentication Documentation

## Overview

This app provides HTTP-only cookie-based authentication for the server-mvp project. Sessions are managed securely using Django's session framework with HTTP-only cookies to prevent XSS attacks.

## Authentication Endpoints

### Login
**Endpoint:** `POST /users/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "root_admin",
    "clientId": null,
    "clientName": null
  }
}
```

**Error Response (401):**
```json
{
  "message": "Invalid credentials"
}
```

**Notes:**
- Sets HTTP-only session cookie automatically
- Cookie has 24-hour expiration
- SameSite=Lax for CSRF protection

### Logout
**Endpoint:** `POST /users/logout/`

**Authentication:** Required (session cookie)

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Notes:**
- Requires CSRF token in header: `X-CSRFToken: <token>`
- Clears session cookie

### Get Current User
**Endpoint:** `GET /users/me/`

**Authentication:** Required (session cookie)

**Success Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "client_admin",
    "clientId": 5,
    "clientName": "Acme Corp"
  }
}
```

## User Roles

The system supports three user roles:

1. **root_admin**: Full system access, can manage all clients and users
2. **client_admin**: Administrator for a specific client organization
3. **client_user**: Regular user within a client organization

## Security Features

- **HTTP-only cookies**: Prevents JavaScript access to session tokens (XSS protection)
- **SameSite=Lax**: Prevents CSRF attacks
- **Session timeout**: 24 hours
- **CSRF protection**: Required for all state-changing operations
- **Secure passwords**: Django's built-in password validation

## Settings Configuration

Key settings in `myproject/settings.py`:

```python
# Session Configuration
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_AGE = 86400  # 24 hours

# CSRF Configuration
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

## Testing

Run the test suite:

```bash
python manage.py test users
```

All tests are located in `users/tests.py` and cover:
- Login with valid/invalid credentials
- Role-based authentication
- Session management
- Logout functionality
- Error handling

## Production Deployment

Before deploying to production:

1. Set `SESSION_COOKIE_SECURE = True` in settings
2. Set `CSRF_COOKIE_SECURE = True` in settings
3. Ensure HTTPS is enabled
4. Update `SECRET_KEY` to a secure random value
5. Set `DEBUG = False`
6. Configure `ALLOWED_HOSTS` appropriately

## Client Integration Example

### JavaScript/Fetch API

```javascript
// Login
async function login(email, password) {
  const response = await fetch('/users/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Important: include cookies
    body: JSON.stringify({ email, password })
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log('Logged in as:', data.user);
    return data.user;
  } else {
    throw new Error('Login failed');
  }
}

// Get current user
async function getCurrentUser() {
  const response = await fetch('/users/me/', {
    credentials: 'include', // Important: include cookies
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.user;
  } else {
    throw new Error('Not authenticated');
  }
}

// Logout (requires CSRF token)
async function logout(csrfToken) {
  const response = await fetch('/users/logout/', {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
    },
    credentials: 'include',
  });
  
  if (response.ok) {
    console.log('Logged out successfully');
  }
}
```

### cURL Example

```bash
# Login
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  -c cookies.txt

# Get current user
curl -X GET http://localhost:8000/users/me/ \
  -b cookies.txt

# Logout
CSRF_TOKEN=$(grep csrftoken cookies.txt | awk '{print $7}')
curl -X POST http://localhost:8000/users/logout/ \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -b cookies.txt
```

## Troubleshooting

### "CSRF Failed: CSRF token missing"
- Ensure you're including the CSRF token in the `X-CSRFToken` header for POST requests
- The CSRF token is available in the `csrftoken` cookie

### "Authentication credentials were not provided"
- Check that cookies are being sent with requests (`credentials: 'include'` in fetch)
- Verify the session cookie hasn't expired

### Session not persisting
- Ensure cookies are enabled in the client
- Check that `credentials: 'include'` is set in fetch requests
- Verify the server and client are on the same domain (or CORS is configured correctly)
