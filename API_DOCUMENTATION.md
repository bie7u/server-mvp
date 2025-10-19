# API Documentation

This document describes all the API endpoints required for the FlowDesk SaaS application. All endpoints require authentication (except login) via JWT tokens stored in HTTP-only cookies.

## Authentication

### Overview

The API uses JWT (JSON Web Token) authentication with HTTP-only cookies for enhanced security. This approach protects against XSS attacks by preventing JavaScript from accessing the tokens.

**Key Features:**
- Access tokens (short-lived: 15 minutes) - stored in `access_token` cookie
- Refresh tokens (long-lived: 7 days) - stored in `refresh_token` cookie
- HTTP-only cookies prevent XSS attacks
- Automatic token rotation on refresh
- Supports both cookie and Authorization header authentication

### POST /api/login
Authenticate a user and receive JWT tokens in HTTP-only cookies.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "root_admin",
    "clientId": null,
    "clientName": null
  }
}
```

**Cookies Set:**
- `access_token`: JWT access token (HTTP-only, expires in 15 minutes)
- `refresh_token`: JWT refresh token (HTTP-only, expires in 7 days)

**Response (401):**
```json
{
  "message": "Invalid credentials"
}
```

**Response (400):**
```json
{
  "message": "Email and password are required"
}
```

---

### POST /api/logout
Logout user and clear authentication cookies.

**Authentication Required:** Yes

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

**Notes:** This endpoint clears the `access_token` and `refresh_token` cookies.

---

### POST /api/refresh
Refresh the access token using the refresh token from cookies.

**Authentication Required:** No (uses refresh token from cookie)

**Response (200):**
```json
{
  "message": "Token refreshed successfully"
}
```

**Cookies Updated:**
- `access_token`: New JWT access token
- `refresh_token`: New JWT refresh token (if rotation enabled)

**Response (401):**
```json
{
  "message": "Refresh token not found"
}
```

or

```json
{
  "message": "Invalid or expired refresh token"
}
```

**Usage:** Call this endpoint when the access token expires (typically handled automatically by the frontend).

---

### GET /api/me
Get current authenticated user information.

**Authentication Required:** Yes

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "client_admin",
    "clientId": 1,
    "clientName": "Acme Corporation"
  }
}
```

**Response (401):**
```json
{
  "message": "Authentication required"
}
```

---

### Authentication Flow

#### 1. Initial Login

**Using cURL:**
```bash
# Login and save cookies to file
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c cookies.txt \
  -v
```

**Response:**
```
HTTP/1.1 200 OK
Set-Cookie: access_token=<jwt>; HttpOnly; Path=/; SameSite=Lax; Max-Age=900
Set-Cookie: refresh_token=<jwt>; HttpOnly; Path=/; SameSite=Lax; Max-Age=604800
Content-Type: application/json

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

#### 2. Authenticated Requests

**Using cURL with cookies:**
```bash
# Get current user info - cookies sent automatically from file
curl http://localhost:8000/api/me/ \
  -b cookies.txt

# Get predictions (authenticated endpoint)
curl http://localhost:8000/predictions/predictions/ \
  -b cookies.txt
```

**Using Authorization Header (alternative):**
```bash
# Extract token from cookie file or login response
ACCESS_TOKEN="<your_jwt_token>"

# Make authenticated request
curl http://localhost:8000/api/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

#### 3. Token Refresh

**Using cURL:**
```bash
# Refresh access token using refresh token from cookies
curl -X POST http://localhost:8000/api/refresh/ \
  -b cookies.txt \
  -c cookies.txt \
  -v
```

**Response:**
```
HTTP/1.1 200 OK
Set-Cookie: access_token=<new_jwt>; HttpOnly; Path=/; SameSite=Lax; Max-Age=900
Set-Cookie: refresh_token=<new_jwt>; HttpOnly; Path=/; SameSite=Lax; Max-Age=604800
Content-Type: application/json

{
  "message": "Token refreshed successfully"
}
```

#### 4. Logout

**Using cURL:**
```bash
# Logout and clear cookies
curl -X POST http://localhost:8000/api/logout/ \
  -b cookies.txt \
  -v
```

**Response:**
```
HTTP/1.1 200 OK
Set-Cookie: access_token=; Max-Age=0; Path=/
Set-Cookie: refresh_token=; Max-Age=0; Path=/
Content-Type: application/json

{
  "message": "Logout successful"
}
```

---

### Security Best Practices

**HTTP-Only Cookies:**
- Tokens are stored in HTTP-only cookies, preventing JavaScript access
- Protects against XSS (Cross-Site Scripting) attacks

**Secure Flag:**
- Cookies use the Secure flag in production (HTTPS only)
- Prevents man-in-the-middle attacks

**SameSite Attribute:**
- Set to 'Lax' to prevent CSRF attacks
- Allows cookies to be sent with top-level navigation

**Token Expiration:**
- Access tokens expire in 15 minutes (short-lived)
- Refresh tokens expire in 7 days (long-lived)
- Automatic rotation prevents token reuse

**Fallback Authentication:**
- API also supports Bearer token in Authorization header
- Use `Authorization: Bearer <token>` for non-browser clients

**Example with Authorization Header:**
```bash
curl -H "Authorization: Bearer <access_token>" https://api.example.com/api/me
```

---

**Roles:**
- `root_admin`: Full access to all data and features
- `client_admin`: Access to specific client data and user management
- `client_user`: Limited access to predictions and rankings

---

## Administration

### GET /admin-panel/clients/
Get list of all client organizations.

**Authentication Required:** Yes (Admin only)

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Acme Corporation",
    "admin_name": "Bob Admin",
    "admin_email": "admin@client.com",
    "created_at": "2025-10-19T10:30:00Z",
    "updated_at": "2025-10-19T10:30:00Z"
  }
]
```

**Access Control:**
- Allowed roles: Admin users only (`is_staff=True`)

---

### POST /admin-panel/clients/
Create a new client organization with a root admin user.

**Authentication Required:** Yes (Admin only)

**Request Body:**
```json
{
  "name": "New Corp",
  "admin_name": "Jane Doe",
  "admin_email": "jane@newcorp.com",
  "client_root_admin_username": "jane_admin",
  "password": "securepassword"
}
```

**Response (201):**
```json
{
  "id": 3,
  "name": "New Corp",
  "admin_name": "Jane Doe",
  "admin_email": "jane@newcorp.com",
  "created_at": "2025-10-19T14:30:00Z",
  "updated_at": "2025-10-19T14:30:00Z"
}
```

**Notes:**
- Automatically creates a Django user with the specified username and password
- Creates a ClientUserM entry linking the user to the client with `client_admin` role
- Sets `is_root_client_admin=True` for the admin user

**Access Control:**
- Allowed roles: Admin users only

---

### GET /admin-panel/clients/{id}/
Get a specific client by ID.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `id`: Client ID

**Response (200):**
```json
{
  "id": 1,
  "name": "Acme Corporation",
  "admin_name": "Bob Admin",
  "admin_email": "admin@client.com",
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T10:30:00Z"
}
```

**Response (404):**
```json
{
  "detail": "Not found."
}
```

**Access Control:**
- Allowed roles: Admin users only

---

### PUT/PATCH /admin-panel/clients/{id}/
Update a client organization.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `id`: Client ID

**Request Body (PUT - all fields required):**
```json
{
  "name": "Updated Corp Name",
  "admin_name": "Jane Doe",
  "admin_email": "jane@updated.com"
}
```

**Request Body (PATCH - partial update):**
```json
{
  "name": "Updated Corp Name"
}
```

**Response (200):**
```json
{
  "id": 1,
  "name": "Updated Corp Name",
  "admin_name": "Bob Admin",
  "admin_email": "admin@client.com",
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T14:45:00Z"
}
```

**Access Control:**
- Allowed roles: Admin users only

---

### GET /admin-panel/clients/{client_pk}/client-users/
Get all users belonging to a specific client.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `client_pk`: Client ID

**Response (200):**
```json
[
  {
    "id": 1,
    "role": "client_admin",
    "client": 1,
    "created_at": "2025-10-19T10:30:00Z",
    "updated_at": "2025-10-19T10:30:00Z",
    "user_read": {
      "id": 2,
      "username": "bob_admin",
      "email": "bob@client.com",
      "first_name": "Bob",
      "last_name": "Admin",
      "is_staff": false,
      "is_active": true
    }
  }
]
```

**Access Control:**
- Allowed roles: Admin users only

---

### POST /admin-panel/clients/{client_pk}/client-users/
Create a new user for a specific client.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `client_pk`: Client ID

**Request Body:**
```json
{
  "role": "client_user",
  "username": "john_user",
  "password": "securepassword"
}
```

**Response (201):**
```json
{
  "id": 5,
  "role": "client_user",
  "client": 1,
  "created_at": "2025-10-19T14:50:00Z",
  "updated_at": "2025-10-19T14:50:00Z",
  "user_read": {
    "id": 6,
    "username": "john_user",
    "email": "",
    "first_name": "",
    "last_name": "",
    "is_staff": false,
    "is_active": true
  }
}
```

**Notes:**
- Automatically creates a Django user with the specified username and password
- Links the user to the specified client
- Role must be either `client_admin` or `client_user`

**Validation:**
- Username must be unique
- Password is required for user creation

**Access Control:**
- Allowed roles: Admin users only

---

### GET /admin-panel/clients/{client_pk}/client-users/{id}/
Get a specific client user.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `client_pk`: Client ID
- `id`: ClientUserM ID

**Response (200):**
```json
{
  "id": 1,
  "role": "client_admin",
  "client": 1,
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T10:30:00Z",
  "user_read": {
    "id": 2,
    "username": "bob_admin",
    "email": "bob@client.com",
    "first_name": "Bob",
    "last_name": "Admin",
    "is_staff": false,
    "is_active": true
  }
}
```

**Access Control:**
- Allowed roles: Admin users only

---

### PUT/PATCH /admin-panel/clients/{client_pk}/client-users/{id}/
Update a client user.

**Authentication Required:** Yes (Admin only)

**URL Parameters:**
- `client_pk`: Client ID
- `id`: ClientUserM ID

**Request Body (PATCH - partial update):**
```json
{
  "role": "client_admin"
}
```

**Response (200):**
```json
{
  "id": 1,
  "role": "client_admin",
  "client": 1,
  "created_at": "2025-10-19T10:30:00Z",
  "updated_at": "2025-10-19T14:55:00Z",
  "user_read": {
    "id": 2,
    "username": "bob_admin",
    "email": "bob@client.com",
    "first_name": "Bob",
    "last_name": "Admin",
    "is_staff": false,
    "is_active": true
  }
}
```

**Access Control:**
- Allowed roles: Admin users only

---

## Leagues

### GET /leagues/standings/
Get league standings (table/classification).

**Authentication Required:** No (publicly accessible)

**Query Parameters:**
- `league` (optional): Filter by league ID
- `season` (optional): Filter by season ID

**Response (200):**
```json
[
  {
    "id": 1,
    "league": 1,
    "league_name": "Premier League",
    "season": 1,
    "season_name": "2024/2025",
    "entries": [
      {
        "id": 1,
        "team": 1,
        "team_name": "Manchester City",
        "position": 1,
        "played_games": 10,
        "won": 8,
        "draw": 1,
        "lost": 1,
        "points": 25,
        "goals_for": 28,
        "goals_against": 8,
        "goal_difference": 20
      }
    ]
  }
]
```

**Notes:**
- Returns standings ordered by position
- Filterable by league and season
- No pagination (returns all standings)

---

### GET /leagues/standings/{id}/
Get a specific standing by ID.

**Authentication Required:** No

**URL Parameters:**
- `id`: Standing ID

**Response (200):**
```json
{
  "id": 1,
  "league": 1,
  "league_name": "Premier League",
  "season": 1,
  "season_name": "2024/2025",
  "entries": [
    {
      "id": 1,
      "team": 1,
      "team_name": "Manchester City",
      "position": 1,
      "played_games": 10,
      "won": 8,
      "draw": 1,
      "lost": 1,
      "points": 25,
      "goals_for": 28,
      "goals_against": 8,
      "goal_difference": 20
    }
  ]
}
```

---

### GET /leagues/rounds/
Get league rounds (matchweeks/game weeks).

**Authentication Required:** No

**Query Parameters:**
- `league` (optional): Filter by league ID
- `season` (optional): Filter by season ID

**Response (200):**
```json
[
  {
    "id": 1,
    "league": 1,
    "league_name": "Premier League",
    "season": 1,
    "season_name": "2024/2025",
    "round_number": 10,
    "name": "Round 10",
    "start_date": "2025-10-18T12:00:00Z",
    "end_date": "2025-10-20T20:00:00Z",
    "matches": [
      {
        "id": 1,
        "home_team": 1,
        "home_team_name": "Manchester City",
        "away_team": 2,
        "away_team_name": "Arsenal",
        "home_score": null,
        "away_score": null,
        "status": "SCHEDULED",
        "date": "2025-10-19T15:00:00Z",
        "league": 1,
        "league_name": "Premier League"
      }
    ]
  }
]
```

**Notes:**
- Returns rounds ordered by round_number
- Includes all matches in each round
- No pagination

---

### GET /leagues/rounds/{id}/
Get a specific round by ID.

**Authentication Required:** No

**URL Parameters:**
- `id`: Round ID

**Response (200):**
```json
{
  "id": 1,
  "league": 1,
  "league_name": "Premier League",
  "season": 1,
  "season_name": "2024/2025",
  "round_number": 10,
  "name": "Round 10",
  "start_date": "2025-10-18T12:00:00Z",
  "end_date": "2025-10-20T20:00:00Z",
  "matches": [
    {
      "id": 1,
      "home_team": 1,
      "home_team_name": "Manchester City",
      "away_team": 2,
      "away_team_name": "Arsenal",
      "home_score": null,
      "away_score": null,
      "status": "SCHEDULED",
      "date": "2025-10-19T15:00:00Z",
      "league": 1,
      "league_name": "Premier League"
    }
  ]
}
```

---

### GET /leagues/upcoming-matches/
Get upcoming matches in the next 7 days.

**Authentication Required:** No

**Query Parameters:**
- `league` (optional): Filter by league ID

**Response (200):**
```json
[
  {
    "id": 1,
    "home_team": 1,
    "home_team_name": "Manchester City",
    "away_team": 2,
    "away_team_name": "Arsenal",
    "home_score": null,
    "away_score": null,
    "status": "SCHEDULED",
    "date": "2025-10-19T15:00:00Z",
    "league": 1,
    "league_name": "Premier League"
  }
]
```

**Notes:**
- Returns matches with date between now and 7 days from now
- Ordered by date (ascending)
- No pagination (returns all upcoming matches)
- Filterable by league

**Match Status Values:**
- `SCHEDULED`: Match is scheduled
- `TIMED`: Match has a specific time set
- `IN_PLAY`: Match is currently being played
- `PAUSED`: Match is paused (halftime, etc.)
- `FINISHED`: Match is finished
- `SUSPENDED`: Match is suspended
- `POSTPONED`: Match is postponed
- `CANCELLED`: Match is cancelled

---

## Predictions

### GET /predictions/predictions/
Get predictions (current user's predictions or all if admin).

**Authentication Required:** Yes

**Response (200):**
```json
[
  {
    "id": 1,
    "user": 2,
    "match": 1,
    "predicted_home_score": 2,
    "predicted_away_score": 1,
    "created_at": "2025-10-18T14:30:00Z",
    "points_awarded": null,
    "status": "pending"
  }
]
```

**Server-Side Filtering:**
- Regular users see only their own predictions
- Admin users (`is_staff=True`) see all predictions

**Notes:**
- No pagination
- Status values: `pending`, `correct_result`, `correct_winner`, `incorrect`, `late`

---

### POST /predictions/predictions/
Create a new prediction for a match.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "match": 1,
  "predicted_home_score": 2,
  "predicted_away_score": 1
}
```

**Response (201):**
```json
{
  "id": 8,
  "user": 3,
  "match": 1,
  "predicted_home_score": 2,
  "predicted_away_score": 1,
  "created_at": "2025-10-19T14:30:00Z",
  "points_awarded": null,
  "status": "pending"
}
```

**Validation:**
- Match must exist and have status `SCHEDULED` or `TIMED`
- Match must not have started yet (date must be in the future)
- User can only have one prediction per match (enforced by database constraint)
- Scores must be non-negative integers

**Response (400) - Validation Error:**
```json
{
  "match": ["You can only predict matches with status SCHEDULED or TIMED."]
}
```

or

```json
{
  "non_field_errors": ["You have already predicted this match."]
}
```

---

### GET /predictions/predictions/{id}/
Get a specific prediction by ID.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Prediction ID

**Response (200):**
```json
{
  "id": 1,
  "user": 2,
  "match": 1,
  "predicted_home_score": 2,
  "predicted_away_score": 1,
  "created_at": "2025-10-18T14:30:00Z",
  "points_awarded": null,
  "status": "pending"
}
```

**Access Control:**
- Users can only see their own predictions
- Admin users can see any prediction

---

### PUT/PATCH /predictions/predictions/{id}/
Update an existing prediction.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Prediction ID

**Request Body (PATCH):**
```json
{
  "predicted_home_score": 3,
  "predicted_away_score": 1
}
```

**Response (200):**
```json
{
  "id": 1,
  "user": 2,
  "match": 1,
  "predicted_home_score": 3,
  "predicted_away_score": 1,
  "created_at": "2025-10-18T14:30:00Z",
  "points_awarded": null,
  "status": "pending"
}
```

**Validation:**
- Same validation rules as POST (match must not have started, etc.)
- Users can only update their own predictions

**Access Control:**
- Users can only update their own predictions
- Admin users can update any prediction

---

### DELETE /predictions/predictions/{id}/
Delete a prediction.

**Authentication Required:** Yes

**URL Parameters:**
- `id`: Prediction ID

**Response (204):**
No content

**Access Control:**
- Users can only delete their own predictions
- Admin users can delete any prediction

---

### GET /predictions/client-rankings/
Get prediction rankings for the current user's client.

**Authentication Required:** Yes

**Response (200):**
```json
[
  {
    "user": 2,
    "username": "bob_admin",
    "points": 15,
    "position": 1
  },
  {
    "user": 3,
    "username": "john_user",
    "points": 12,
    "position": 2
  }
]
```

**Server-Side Filtering:**
- Returns rankings for the authenticated user's client
- If user is not associated with a client, returns empty list
- Ordered by position (ascending)

**Notes:**
- No pagination
- Rankings are calculated based on prediction accuracy
- Points are awarded based on prediction results

---

## Error Responses

All endpoints may return the following error responses:

### 401 Unauthorized
```json
{
  "message": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "message": "Access denied - insufficient permissions"
}
```

### 404 Not Found
```json
{
  "message": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "message": "Invalid request parameters",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "message": "Internal server error"
}
```

---

## Client Integration Examples

### JavaScript/TypeScript Frontend

#### Using Fetch API

```javascript
// api.js - API client module
const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  /**
   * Login user and store cookies
   */
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/api/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
      credentials: 'include' // Important: include cookies
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }
    
    return response.json();
  }
  
  /**
   * Get current user info
   */
  async getCurrentUser() {
    const response = await fetch(`${API_BASE_URL}/api/me/`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get user info');
    }
    
    return response.json();
  }
  
  /**
   * Refresh access token
   */
  async refreshToken() {
    const response = await fetch(`${API_BASE_URL}/api/refresh/`, {
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
   */
  async logout() {
    const response = await fetch(`${API_BASE_URL}/api/logout/`, {
      method: 'POST',
      credentials: 'include'
    });
    
    return response.ok;
  }
  
  /**
   * Get upcoming matches
   */
  async getUpcomingMatches(leagueId = null) {
    const url = new URL(`${API_BASE_URL}/leagues/upcoming-matches/`);
    if (leagueId) {
      url.searchParams.append('league', leagueId);
    }
    
    const response = await fetch(url, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get matches');
    }
    
    return response.json();
  }
  
  /**
   * Create a prediction
   */
  async createPrediction(matchId, predictedHomeScore, predictedAwayScore) {
    const response = await fetch(`${API_BASE_URL}/predictions/predictions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        match: matchId,
        predicted_home_score: predictedHomeScore,
        predicted_away_score: predictedAwayScore
      }),
      credentials: 'include'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create prediction');
    }
    
    return response.json();
  }
  
  /**
   * Get user's predictions
   */
  async getMyPredictions() {
    const response = await fetch(`${API_BASE_URL}/predictions/predictions/`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get predictions');
    }
    
    return response.json();
  }
  
  /**
   * Get client rankings
   */
  async getClientRankings() {
    const response = await fetch(`${API_BASE_URL}/predictions/client-rankings/`, {
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error('Failed to get rankings');
    }
    
    return response.json();
  }
  
  /**
   * Get league standings
   */
  async getStandings(leagueId = null, seasonId = null) {
    const url = new URL(`${API_BASE_URL}/leagues/standings/`);
    if (leagueId) url.searchParams.append('league', leagueId);
    if (seasonId) url.searchParams.append('season', seasonId);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error('Failed to get standings');
    }
    
    return response.json();
  }
}

// Export singleton instance
export const api = new ApiClient();
```

#### Usage in React Component

```jsx
import React, { useState, useEffect } from 'react';
import { api } from './api';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  
  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    
    try {
      const data = await api.login(email, password);
      console.log('Logged in:', data.user);
      // Redirect to dashboard or update app state
    } catch (err) {
      setError(err.message);
    }
  };
  
  return (
    <form onSubmit={handleLogin}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button type="submit">Login</button>
      {error && <div className="error">{error}</div>}
    </form>
  );
}

function PredictionsPage() {
  const [matches, setMatches] = useState([]);
  const [predictions, setPredictions] = useState([]);
  
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      const [matchesData, predictionsData] = await Promise.all([
        api.getUpcomingMatches(),
        api.getMyPredictions()
      ]);
      setMatches(matchesData);
      setPredictions(predictionsData);
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  };
  
  const handlePredict = async (matchId, homeScore, awayScore) => {
    try {
      await api.createPrediction(matchId, homeScore, awayScore);
      loadData(); // Reload data
    } catch (err) {
      alert('Failed to create prediction: ' + err.message);
    }
  };
  
  return (
    <div>
      <h1>Make Your Predictions</h1>
      {/* Render matches and prediction form */}
    </div>
  );
}
```

### Python Client

```python
import requests
from typing import Optional, Dict, Any, List

class APIClient:
    """Python client for the prediction API with HTTP-only cookie authentication."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and store cookies in session."""
        response = self.session.post(
            f"{self.base_url}/api/login/",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        return response.json()
    
    def logout(self) -> bool:
        """Logout and clear cookies."""
        response = self.session.post(f"{self.base_url}/api/logout/")
        return response.status_code == 200
    
    def refresh_token(self) -> Dict[str, Any]:
        """Refresh the access token."""
        response = self.session.post(f"{self.base_url}/api/refresh/")
        response.raise_for_status()
        return response.json()
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information."""
        response = self.session.get(f"{self.base_url}/api/me/")
        response.raise_for_status()
        return response.json()
    
    def get_upcoming_matches(self, league_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get upcoming matches."""
        params = {"league": league_id} if league_id else {}
        response = self.session.get(
            f"{self.base_url}/leagues/upcoming-matches/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_prediction(
        self, 
        match_id: int, 
        predicted_home_score: int, 
        predicted_away_score: int
    ) -> Dict[str, Any]:
        """Create a new prediction."""
        response = self.session.post(
            f"{self.base_url}/predictions/predictions/",
            json={
                "match": match_id,
                "predicted_home_score": predicted_home_score,
                "predicted_away_score": predicted_away_score
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_my_predictions(self) -> List[Dict[str, Any]]:
        """Get current user's predictions."""
        response = self.session.get(f"{self.base_url}/predictions/predictions/")
        response.raise_for_status()
        return response.json()
    
    def update_prediction(
        self,
        prediction_id: int,
        predicted_home_score: int,
        predicted_away_score: int
    ) -> Dict[str, Any]:
        """Update an existing prediction."""
        response = self.session.patch(
            f"{self.base_url}/predictions/predictions/{prediction_id}/",
            json={
                "predicted_home_score": predicted_home_score,
                "predicted_away_score": predicted_away_score
            }
        )
        response.raise_for_status()
        return response.json()
    
    def delete_prediction(self, prediction_id: int) -> bool:
        """Delete a prediction."""
        response = self.session.delete(
            f"{self.base_url}/predictions/predictions/{prediction_id}/"
        )
        return response.status_code == 204
    
    def get_client_rankings(self) -> List[Dict[str, Any]]:
        """Get rankings for current user's client."""
        response = self.session.get(f"{self.base_url}/predictions/client-rankings/")
        response.raise_for_status()
        return response.json()
    
    def get_standings(
        self, 
        league_id: Optional[int] = None,
        season_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get league standings."""
        params = {}
        if league_id:
            params["league"] = league_id
        if season_id:
            params["season"] = season_id
        
        response = self.session.get(
            f"{self.base_url}/leagues/standings/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    # Admin endpoints (require admin authentication)
    
    def create_client(
        self,
        name: str,
        admin_name: str,
        admin_email: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """Create a new client (admin only)."""
        response = self.session.post(
            f"{self.base_url}/admin-panel/clients/",
            json={
                "name": name,
                "admin_name": admin_name,
                "admin_email": admin_email,
                "client_root_admin_username": username,
                "password": password
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients (admin only)."""
        response = self.session.get(f"{self.base_url}/admin-panel/clients/")
        response.raise_for_status()
        return response.json()
    
    def create_client_user(
        self,
        client_id: int,
        username: str,
        password: str,
        role: str = "client_user"
    ) -> Dict[str, Any]:
        """Create a new user for a client (admin only)."""
        response = self.session.post(
            f"{self.base_url}/admin-panel/clients/{client_id}/client-users/",
            json={
                "username": username,
                "password": password,
                "role": role
            }
        )
        response.raise_for_status()
        return response.json()


# Usage example
if __name__ == "__main__":
    client = APIClient()
    
    # Login
    user_data = client.login("user@example.com", "password123")
    print(f"Logged in as: {user_data['user']['name']}")
    
    # Get upcoming matches
    matches = client.get_upcoming_matches()
    print(f"Found {len(matches)} upcoming matches")
    
    # Create a prediction
    if matches:
        prediction = client.create_prediction(
            match_id=matches[0]['id'],
            predicted_home_score=2,
            predicted_away_score=1
        )
        print(f"Created prediction: {prediction}")
    
    # Get rankings
    rankings = client.get_client_rankings()
    print(f"Rankings: {rankings}")
    
    # Logout
    client.logout()
    print("Logged out")
```

### cURL Examples for Testing

```bash
#!/bin/bash
# Complete API testing script

BASE_URL="http://localhost:8000"
COOKIES_FILE="cookies.txt"

echo "=== 1. Login ==="
curl -X POST "$BASE_URL/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}' \
  -c "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 2. Get Current User ==="
curl "$BASE_URL/api/me/" \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 3. Get Upcoming Matches ==="
curl "$BASE_URL/leagues/upcoming-matches/" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 4. Get League Standings ==="
curl "$BASE_URL/leagues/standings/" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 5. Create Prediction ==="
curl -X POST "$BASE_URL/predictions/predictions/" \
  -H "Content-Type: application/json" \
  -d '{"match":1,"predicted_home_score":2,"predicted_away_score":1}' \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 6. Get My Predictions ==="
curl "$BASE_URL/predictions/predictions/" \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 7. Get Client Rankings ==="
curl "$BASE_URL/predictions/client-rankings/" \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 8. Refresh Token ==="
curl -X POST "$BASE_URL/api/refresh/" \
  -b "$COOKIES_FILE" \
  -c "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 9. Logout ==="
curl -X POST "$BASE_URL/api/logout/" \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=== 10. Try Accessing After Logout (should fail) ==="
curl "$BASE_URL/api/me/" \
  -b "$COOKIES_FILE" \
  -w "\nHTTP Status: %{http_code}\n\n"

# Clean up
rm -f "$COOKIES_FILE"
```

---

## Implementation Notes

### Authentication Flow
1. Client sends credentials to `/api/login/`
2. Server validates credentials and returns user data with HTTP-only cookies
3. Client stores cookies automatically (browser handles this)
4. Client includes cookies in all subsequent requests automatically
5. Server validates token from cookie and extracts user info
6. When access token expires, client calls `/api/refresh/` to get new tokens
7. Server validates refresh token and issues new access and refresh tokens

### Access Control
- **Admin endpoints** (`/admin-panel/*`): Require `is_staff=True`
- **Prediction endpoints** (`/predictions/*`): Require authentication, users see only their own data
- **League endpoints** (`/leagues/*`): Publicly accessible (no authentication required)
- **Auth endpoints** (`/api/login/`, `/api/me/`, etc.): Login is public, others require authentication

---

## Database Schema

### Django Models

The API uses Django ORM with the following models:

**ClientM** (users.models)
- `id`: Primary key
- `name`: Client organization name
- `admin_name`: Name of the admin user
- `admin_email`: Email of the admin user
- `status`: 'active' or 'inactive'
- `created_at`, `updated_at`: Timestamps

**ClientUserM** (users.models)
- `id`: Primary key
- `user`: OneToOne to Django User model
- `role`: 'client_admin' or 'client_user'
- `client`: Foreign key to ClientM
- `is_root_client_admin`: Boolean
- `created_at`, `updated_at`: Timestamps

**LeagueM, SeasonM, TeamM** (leagues.models)
- League, season, and team information

**MatchM** (leagues.models)
- `id`: Primary key
- `home_team`, `away_team`: Foreign keys to TeamM
- `home_score`, `away_score`: Integer scores (nullable)
- `status`: Match status (SCHEDULED, FINISHED, etc.)
- `date`: Match date/time
- `league`, `season`, `round`: Foreign keys
- `created_at`, `updated_at`: Timestamps

**PredictionM** (predictions.models)
- `id`: Primary key
- `user`: Foreign key to Django User
- `match`: Foreign key to MatchM
- `predicted_home_score`, `predicted_away_score`: Integer predictions
- `points_awarded`: Points earned (nullable)
- `status`: 'pending', 'correct_result', 'correct_winner', 'incorrect', 'late'
- `created_at`: Timestamp
- Unique constraint on (user, match)

**ClientRankingM, ClientRankingEntryM** (predictions.models)
- Stores ranking snapshots for each client

---

## Security Considerations

1. **HTTP-Only Cookies**: Tokens stored in HTTP-only cookies prevent XSS attacks
2. **Token Expiration**: Access tokens expire in 15 minutes, refresh tokens in 7 days
3. **Token Rotation**: Refresh tokens are rotated on use for enhanced security
4. **HTTPS Required**: In production, cookies are sent only over HTTPS
5. **SameSite Attribute**: Set to 'Lax' to prevent CSRF attacks
6. **Password Hashing**: Django uses PBKDF2 by default for password hashing
7. **Admin Endpoints**: Protected with `IsAdminUser` permission class
8. **User Data Isolation**: Users can only see their own predictions and client data

---

## CORS Configuration

For cross-origin requests (e.g., frontend on different domain), configure CORS in Django:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

# Allow specific origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://yourdomain.com",
]

# Allow credentials (cookies)
CORS_ALLOW_CREDENTIALS = True
```

Install: `pip install django-cors-headers`
