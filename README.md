# server-mvp

A Django-based REST API server with HTTP-only cookie JWT authentication for secure token management.

## Features

- **Secure Authentication**: HTTP-only cookies prevent XSS attacks
- **JWT Tokens**: Access tokens (15 min) and refresh tokens (7 days)
- **Automatic Token Rotation**: Enhanced security with token rotation on refresh
- **Dual Authentication Support**: Cookie-based and Authorization header
- **Django REST Framework**: Comprehensive API with pagination and filtering
- **Test Coverage**: Full test suite for authentication flow

## Authentication

### Quick Start

The API uses JWT authentication with HTTP-only cookies. This provides protection against XSS attacks by preventing JavaScript access to authentication tokens.

#### Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  -c cookies.txt
```

Response includes user data and sets HTTP-only cookies:
- `access_token`: Short-lived (15 minutes)
- `refresh_token`: Long-lived (7 days)

#### Authenticated Requests
```bash
# Use cookies automatically
curl http://localhost:8000/api/me/ -b cookies.txt

# Or use Authorization header
curl http://localhost:8000/api/me/ \
  -H "Authorization: Bearer <access_token>"
```

#### Refresh Token
```bash
curl -X POST http://localhost:8000/api/refresh/ \
  -b cookies.txt \
  -c cookies.txt
```

#### Logout
```bash
curl -X POST http://localhost:8000/api/logout/ \
  -b cookies.txt
```

### Security Features

- **HTTP-only cookies**: Prevents JavaScript access to tokens
- **Secure flag**: HTTPS-only in production
- **SameSite=Lax**: CSRF protection
- **Token expiration**: Short-lived access tokens
- **Token rotation**: Automatic refresh token rotation

## Documentation

### Complete API Documentation
See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for comprehensive API documentation including:
- All endpoint details with request/response examples
- Query parameters and filtering options
- Authentication requirements
- Client integration examples (JavaScript, Python, cURL)
- Database schema
- Security considerations

### Authentication Guide
See [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) for HTTP-only cookie authentication including:
- Complete authentication flow
- Client integration examples (React, Vue.js, Python)
- Troubleshooting common issues
- Testing and integration examples
- Security best practices

## API Endpoints

### Authentication Endpoints
- `POST /api/login/` - Login and receive tokens in HTTP-only cookies
- `POST /api/logout/` - Logout and clear tokens
- `POST /api/refresh/` - Refresh access token
- `GET /api/me/` - Get current user info

### Administration Endpoints (Admin only)
- `GET/POST /admin-panel/clients/` - Manage client organizations
- `GET/PUT/PATCH /admin-panel/clients/{id}/` - Client details and updates
- `GET/POST /admin-panel/clients/{client_pk}/client-users/` - Manage client users
- `GET/PUT/PATCH /admin-panel/clients/{client_pk}/client-users/{id}/` - User details

### Leagues Endpoints (Public)
- `GET /leagues/standings/` - Get league standings/tables
- `GET /leagues/standings/{id}/` - Get specific standing
- `GET /leagues/rounds/` - Get league rounds/matchweeks
- `GET /leagues/rounds/{id}/` - Get specific round with matches
- `GET /leagues/upcoming-matches/` - Get upcoming matches (next 7 days)

### Predictions Endpoints (Authenticated)
- `GET/POST /predictions/predictions/` - View and create predictions
- `GET/PUT/PATCH/DELETE /predictions/predictions/{id}/` - Manage specific prediction
- `GET /predictions/client-rankings/` - Get rankings for user's client

## Installation

```bash
# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-nested-routers

# Run migrations
python manage.py migrate

# Run development server
python manage.py runserver
```

## Testing

```bash
# Run all tests
python manage.py test

# Run authentication tests only
python manage.py test users.test_authentication

# Test all API endpoints
./test_all_endpoints.sh

# Test with example Python client
python example_client.py
```

### Test Coverage
The project includes comprehensive tests for:
- ✅ Authentication flow (login, logout, refresh)
- ✅ HTTP-only cookie handling
- ✅ Token expiration and rotation
- ✅ Role-based access control
- ✅ Prediction creation and validation
- ✅ Client rankings calculation

## Configuration

Key settings in `myproject/settings.py`:

```python
# JWT token lifetimes
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Cookie settings
AUTH_COOKIE = 'access_token'
AUTH_COOKIE_REFRESH = 'refresh_token'
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_SECURE = not DEBUG  # True in production
AUTH_COOKIE_SAMESITE = 'Lax'
```

## Development

The project uses Django 5.2.7 with Django REST Framework for API development.

## License

MIT