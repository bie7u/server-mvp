# Quick Start Guide

Get started with the API in just a few minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/bie7u/server-mvp.git
cd server-mvp
```

2. **Install dependencies**:
```bash
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-nested-routers
```

3. **Run migrations**:
```bash
python manage.py migrate
```

4. **Create a test user**:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from users.models import ClientM, ClientUserM

# Create a client organization
client = ClientM.objects.create(
    name="Test Corporation",
    admin_name="Test Admin",
    admin_email="admin@testcorp.com"
)

# Create a user
user = User.objects.create_user(
    username="testuser",
    email="test@example.com",
    password="testpass123",
    first_name="Test",
    last_name="User"
)

# Link user to client
ClientUserM.objects.create(
    user=user,
    role=ClientUserM.CLIENT_USER,
    client=client
)

print("✓ Test user created successfully!")
print("Email: test@example.com")
print("Password: testpass123")
exit()
```

5. **Start the development server**:
```bash
python manage.py runserver
```

The API is now running at `http://localhost:8000`!

## Test the API

### Option 1: Use the Example Python Client

```bash
python example_client.py
```

Edit the script to use your test credentials:
```python
# In example_client.py, update these lines:
cookies = login("test@example.com", "testpass123")
```

### Option 2: Use cURL

```bash
# Login and save cookies
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' \
  -c cookies.txt \
  -v

# Get current user
curl http://localhost:8000/api/me/ \
  -b cookies.txt

# Get upcoming matches
curl http://localhost:8000/leagues/upcoming-matches/

# Get your predictions
curl http://localhost:8000/predictions/predictions/ \
  -b cookies.txt
```

### Option 3: Run the Test Suite

```bash
# Run all automated tests
python manage.py test

# Run comprehensive endpoint tests
./test_all_endpoints.sh
```

## Quick API Examples

### JavaScript (Browser/Frontend)

```javascript
// Login
const response = await fetch('http://localhost:8000/api/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'testpass123'
  }),
  credentials: 'include' // Important for cookies!
});

const data = await response.json();
console.log('Logged in as:', data.user.name);

// Get current user
const userResponse = await fetch('http://localhost:8000/api/me/', {
  credentials: 'include'
});
const userData = await userResponse.json();
console.log('User:', userData.user);
```

### Python

```python
import requests

# Create session to persist cookies
session = requests.Session()

# Login
response = session.post('http://localhost:8000/api/login/', json={
    'email': 'test@example.com',
    'password': 'testpass123'
})
user = response.json()['user']
print(f"Logged in as: {user['name']}")

# Get predictions
predictions = session.get('http://localhost:8000/predictions/predictions/').json()
print(f"You have {len(predictions)} predictions")
```

## Common Endpoints

### Public Endpoints (No Authentication Required)

```bash
# Get upcoming matches (next 7 days)
GET /leagues/upcoming-matches/

# Get league standings
GET /leagues/standings/

# Get league rounds
GET /leagues/rounds/
```

### Authenticated Endpoints (Login Required)

```bash
# Get current user info
GET /api/me/

# Get your predictions
GET /predictions/predictions/

# Create a prediction
POST /predictions/predictions/
Body: {
  "match": 1,
  "predicted_home_score": 2,
  "predicted_away_score": 1
}

# Get client rankings
GET /predictions/client-rankings/
```

### Admin Endpoints (Admin User Required)

```bash
# Get all clients
GET /admin-panel/clients/

# Create a new client
POST /admin-panel/clients/
Body: {
  "name": "New Corp",
  "admin_name": "Admin Name",
  "admin_email": "admin@newcorp.com",
  "client_root_admin_username": "adminuser",
  "password": "securepassword"
}

# Get client users
GET /admin-panel/clients/{client_id}/client-users/
```

## Next Steps

1. **Read the complete documentation**:
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - All endpoints with detailed examples
   - [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - HTTP-only cookie authentication guide

2. **Create sample data**:
   - Add leagues, teams, and matches via Django admin or shell
   - Create predictions for upcoming matches

3. **Build your frontend**:
   - Use the JavaScript examples in [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)
   - Integrate with React, Vue, or your preferred framework

4. **Deploy to production**:
   - Set `DEBUG = False`
   - Configure HTTPS
   - Set strong `SECRET_KEY`
   - Update `ALLOWED_HOSTS`

## Troubleshooting

### "ModuleNotFoundError: No module named 'django'"
```bash
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-nested-routers
```

### "No such table" error
```bash
python manage.py migrate
```

### "Invalid credentials" when logging in
Make sure you created the test user correctly. Re-run the user creation steps above.

### Cookies not working in browser
- Ensure `credentials: 'include'` in all fetch requests
- Check browser DevTools > Application > Cookies
- If frontend is on different port, configure CORS (see AUTHENTICATION_GUIDE.md)

### Tests failing
```bash
# Make sure database is up to date
python manage.py migrate

# Run tests with verbose output
python manage.py test -v 2
```

## Need Help?

- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed endpoint information
- Review [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) for authentication help
- Run `python example_client.py` to see a working example
- Check the troubleshooting section in AUTHENTICATION_GUIDE.md

## What's Next?

Once you're comfortable with the basics:

1. Create an admin user: `python manage.py createsuperuser`
2. Access Django admin panel: http://localhost:8000/admin/
3. Create leagues, teams, and matches
4. Build a frontend to interact with the API
5. Deploy to production!

Happy coding! 🚀
