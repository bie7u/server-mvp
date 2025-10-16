# API Documentation

This document describes all the API endpoints required for the FlowDesk SaaS application. All endpoints require authentication (except login) via Bearer token in the `Authorization` header.

## Authentication

### POST /api/login
Authenticate a user and receive a token.

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
  "token": "jwt-token-here",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "user@example.com",
    "role": "root_admin"
  }
}
```

**Response (401):**
```json
{
  "message": "Invalid credentials"
}
```

**Roles:**
- `root_admin`: Full access to all data and features
- `client_admin`: Access to specific client data and user management
- `client_user`: Limited access to predictions and rankings

---

## Dashboard

### GET /api/dashboard/stats
Get dashboard statistics.

**Authentication Required:** Yes

**Response (200):**
```json
{
  "totalUsers": 1523,
  "activeClients": 45,
  "revenue": 125430,
  "growth": 12.5
}
```

**Access Control:**
- `root_admin`: Global statistics across all clients
- `client_admin`: Statistics for their client organization
- `client_user`: Statistics for their client organization

---

## Analytics

### GET /api/analytics
Get analytics data for charts and visualization.

**Authentication Required:** Yes

**Query Parameters:**
- `clientId` (optional): Filter analytics by client ID (only for root_admin)
- `startDate` (optional): Start date for analytics range (ISO 8601)
- `endDate` (optional): End date for analytics range (ISO 8601)

**Response (200):**
```json
{
  "data": [
    { "name": "Jan", "users": 400, "revenue": 2400 },
    { "name": "Feb", "users": 300, "revenue": 1398 },
    { "name": "Mar", "users": 600, "revenue": 9800 }
  ]
}
```

**Server-Side Filtering:**
- Filters data based on user role and client assignment
- `root_admin` can view all data or filter by specific client
- `client_admin` and `client_user` see only their client's data

---

## Users

### GET /api/users
Get list of users with server-side filtering.

**Authentication Required:** Yes

**Query Parameters:**
- `clientId` (optional): Filter by client ID
- `role` (optional): Filter by role (`root_admin`, `client_admin`, `client_user`)
- `status` (optional): Filter by status (`active`, `inactive`)
- `search` (optional): Search by name or email
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "users": [
    {
      "id": 1,
      "name": "Alice Root",
      "email": "root@flowdesk.com",
      "role": "root_admin",
      "status": "active",
      "clientId": null,
      "clientName": null
    },
    {
      "id": 2,
      "name": "Bob Admin",
      "email": "admin@client.com",
      "role": "client_admin",
      "status": "active",
      "clientId": 1,
      "clientName": "Acme Corporation"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "totalPages": 5
  }
}
```

**Server-Side Filtering:**
- `root_admin`: Can see all users and filter by any parameter
- `client_admin`: Can only see users from their client
- `client_user`: Cannot access this endpoint

**Access Control:**
- Allowed roles: `root_admin`, `client_admin`

---

### PATCH /api/users/:userId/client
Update a user's client assignment.

**Authentication Required:** Yes

**URL Parameters:**
- `userId`: User ID to update

**Request Body:**
```json
{
  "clientId": 1
}
```

**Response (200):**
```json
{
  "message": "User client updated successfully",
  "userId": 2,
  "clientId": 1
}
```

**Access Control:**
- Allowed roles: `root_admin`

---

### DELETE /api/users/:userId
Delete a user.

**Authentication Required:** Yes

**URL Parameters:**
- `userId`: User ID to delete

**Response (200):**
```json
{
  "message": "User deleted successfully",
  "userId": 2
}
```

**Access Control:**
- Allowed roles: `root_admin`, `client_admin` (can only delete users from their client)

---

## Clients

### GET /api/clients
Get list of all client organizations.

**Authentication Required:** Yes

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `inactive`)
- `search` (optional): Search by client name or admin email
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "clients": [
    {
      "id": 1,
      "name": "Acme Corporation",
      "adminName": "Bob Admin",
      "adminEmail": "admin@client.com",
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 45,
    "totalPages": 5
  }
}
```

**Server-Side Filtering:**
- Filters based on query parameters
- Pagination applied server-side

**Access Control:**
- Allowed roles: `root_admin`

---

### GET /api/clients/:clientId
Get a specific client by ID.

**Authentication Required:** Yes

**URL Parameters:**
- `clientId`: Client ID

**Response (200):**
```json
{
  "client": {
    "id": 1,
    "name": "Acme Corporation",
    "adminName": "Bob Admin",
    "adminEmail": "admin@client.com",
    "status": "active"
  }
}
```

**Response (404):**
```json
{
  "message": "Client not found"
}
```

**Access Control:**
- `root_admin`: Can access any client
- `client_admin`: Can only access their own client

---

### GET /api/clients/:clientId/users
Get all users belonging to a specific client.

**Authentication Required:** Yes

**URL Parameters:**
- `clientId`: Client ID

**Query Parameters:**
- `role` (optional): Filter by role
- `status` (optional): Filter by status
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "users": [
    {
      "id": 2,
      "name": "Bob Admin",
      "email": "admin@client.com",
      "role": "client_admin",
      "status": "active",
      "clientId": 1,
      "clientName": "Acme Corporation"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 3,
    "totalPages": 1
  }
}
```

**Server-Side Filtering:**
- Filters users by client ID and optional query parameters
- Pagination applied server-side

**Access Control:**
- `root_admin`: Can access users from any client
- `client_admin`: Can only access users from their client

---

### POST /api/clients
Create a new client organization.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "clientName": "New Corp",
  "adminName": "Jane Doe",
  "adminEmail": "jane@newcorp.com",
  "adminPassword": "securepassword"
}
```

**Response (200):**
```json
{
  "client": {
    "id": 3,
    "name": "New Corp",
    "adminName": "Jane Doe",
    "adminEmail": "jane@newcorp.com",
    "status": "active"
  },
  "message": "Client created successfully"
}
```

**Access Control:**
- Allowed roles: `root_admin`

---

## Predictions

### GET /api/predictions/matches
Get upcoming matches available for predictions.

**Authentication Required:** Yes

**Query Parameters:**
- `league` (optional): Filter by league name
- `date` (optional): Filter matches by date (ISO 8601)
- `locked` (optional): Filter by locked status (true/false)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "matches": [
    {
      "id": 1,
      "homeTeam": "Manchester City",
      "awayTeam": "Arsenal",
      "date": "2025-10-13",
      "time": "15:00",
      "league": "Premier League",
      "locked": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 8,
    "totalPages": 1
  }
}
```

**Server-Side Filtering:**
- Filters matches based on query parameters
- Pagination applied server-side
- Only returns upcoming matches (not past matches)

---

### GET /api/predictions/user
Get the current user's predictions.

**Authentication Required:** Yes

**Query Parameters:**
- `matchId` (optional): Filter by match ID
- `status` (optional): Filter by match status (`upcoming`, `locked`, `completed`)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "predictions": [
    {
      "id": 1,
      "userId": 2,
      "userName": "Bob Admin",
      "email": "admin@client.com",
      "clientId": 1,
      "matchId": 1,
      "homeScore": 2,
      "awayScore": 1
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 5,
    "totalPages": 1
  }
}
```

**Server-Side Filtering:**
- Returns only predictions for the authenticated user
- Filters based on user's authentication token
- Optional filtering by match ID or status
- Pagination applied server-side

---

### POST /api/predictions
Create a new prediction for a match.

**Authentication Required:** Yes

**Request Body:**
```json
{
  "matchId": 1,
  "homeScore": 2,
  "awayScore": 1
}
```

**Response (200):**
```json
{
  "prediction": {
    "id": 8,
    "userId": 3,
    "userName": "Charlie User",
    "email": "user@client.com",
    "clientId": 1,
    "matchId": 1,
    "homeScore": 2,
    "awayScore": 1
  },
  "message": "Prediction created successfully"
}
```

**Validation:**
- Match must exist and not be locked
- User can only have one prediction per match
- Scores must be non-negative integers

---

### PUT /api/predictions/:predictionId
Update an existing prediction.

**Authentication Required:** Yes

**URL Parameters:**
- `predictionId`: Prediction ID to update

**Request Body:**
```json
{
  "homeScore": 3,
  "awayScore": 1
}
```

**Response (200):**
```json
{
  "prediction": {
    "id": 1,
    "userId": 3,
    "userName": "Charlie User",
    "email": "user@client.com",
    "clientId": 1,
    "matchId": 1,
    "homeScore": 3,
    "awayScore": 1
  },
  "message": "Prediction updated successfully"
}
```

**Response (404):**
```json
{
  "message": "Prediction not found"
}
```

**Validation:**
- User can only update their own predictions
- Match must not be locked
- Scores must be non-negative integers

---

## Rankings

### GET /api/rankings
Get prediction rankings for a client.

**Authentication Required:** Yes

**Query Parameters:**
- `clientId` (optional): Filter by client ID (only for root_admin)
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)

**Response (200):**
```json
{
  "rankings": [
    {
      "position": 1,
      "userId": 2,
      "userName": "Bob Admin",
      "email": "admin@client.com",
      "points": 15,
      "correctResults": 3,
      "correctWinners": 6,
      "totalPredictions": 7
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 3,
    "totalPages": 1
  }
}
```

**Server-Side Filtering:**
- `root_admin`: Can view rankings for any client by specifying clientId
- `client_admin` and `client_user`: Automatically filtered to their client
- Rankings calculated based on prediction points
- Sorting: Primary by points (desc), secondary by correct results (desc)

**Ranking Points System:**
- Exact score prediction: 3 points
- Correct winner prediction: 1 point
- Incorrect prediction: 0 points

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

## Server-Side Filtering Best Practices

1. **Always filter by user role and client assignment** to ensure data isolation
2. **Use query parameters** for optional filtering (status, search, date ranges)
3. **Implement pagination** for all list endpoints to improve performance
4. **Validate all inputs** on the server side
5. **Apply access control** before any data filtering or retrieval
6. **Index database fields** used in filtering for better performance
7. **Sanitize search inputs** to prevent SQL injection or NoSQL injection
8. **Use case-insensitive search** for better user experience
9. **Return consistent response formats** with pagination metadata
10. **Log all filtering operations** for audit and debugging purposes

---

## Implementation Notes

### Authentication Flow
1. Client sends credentials to `/api/login`
2. Server validates credentials and returns JWT token
3. Client stores token in localStorage
4. Client includes token in Authorization header for all subsequent requests
5. Server validates token and extracts user info for filtering

### Access Control Flow
1. Extract user info from JWT token
2. Check if user role has access to the endpoint
3. Apply role-based filtering to queries
4. Return filtered results

### Server-Side Filtering Implementation
```javascript
// Example: Filter users based on role
const getUsers = (requestUser, queryParams) => {
  let filteredUsers = allUsers;
  
  // Role-based filtering
  if (requestUser.role === 'client_admin') {
    filteredUsers = filteredUsers.filter(u => u.clientId === requestUser.clientId);
  }
  
  // Query parameter filtering
  if (queryParams.status) {
    filteredUsers = filteredUsers.filter(u => u.status === queryParams.status);
  }
  
  if (queryParams.search) {
    const search = queryParams.search.toLowerCase();
    filteredUsers = filteredUsers.filter(u => 
      u.name.toLowerCase().includes(search) || 
      u.email.toLowerCase().includes(search)
    );
  }
  
  // Pagination
  const page = parseInt(queryParams.page) || 1;
  const limit = Math.min(parseInt(queryParams.limit) || 10, 100);
  const startIndex = (page - 1) * limit;
  const endIndex = startIndex + limit;
  
  const paginatedUsers = filteredUsers.slice(startIndex, endIndex);
  
  return {
    users: paginatedUsers,
    pagination: {
      page,
      limit,
      total: filteredUsers.length,
      totalPages: Math.ceil(filteredUsers.length / limit)
    }
  };
};
```

---

## Database Schema Recommendations

### Users Table
- `id` (Primary Key)
- `name` (String, indexed)
- `email` (String, unique, indexed)
- `password` (String, hashed)
- `role` (Enum: root_admin, client_admin, client_user, indexed)
- `status` (Enum: active, inactive, indexed)
- `clientId` (Foreign Key, indexed, nullable)
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

### Clients Table
- `id` (Primary Key)
- `name` (String, indexed)
- `adminName` (String)
- `adminEmail` (String, indexed)
- `status` (Enum: active, inactive, indexed)
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

### Matches Table
- `id` (Primary Key)
- `homeTeam` (String)
- `awayTeam` (String)
- `date` (Date, indexed)
- `time` (Time)
- `league` (String, indexed)
- `locked` (Boolean, indexed)
- `actualHomeScore` (Integer, nullable)
- `actualAwayScore` (Integer, nullable)
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)

### Predictions Table
- `id` (Primary Key)
- `userId` (Foreign Key, indexed)
- `matchId` (Foreign Key, indexed)
- `homeScore` (Integer)
- `awayScore` (Integer)
- `points` (Integer, calculated, indexed)
- `createdAt` (Timestamp)
- `updatedAt` (Timestamp)
- Unique constraint on (userId, matchId)

### Indexes for Performance
- `users`: (role, clientId), (email), (status)
- `clients`: (name), (status)
- `matches`: (date, locked), (league)
- `predictions`: (userId, matchId), (matchId)

---

## Rate Limiting Recommendations

Implement rate limiting to prevent abuse:

- **Login endpoint**: 5 requests per minute per IP
- **List endpoints**: 30 requests per minute per user
- **Create/Update endpoints**: 10 requests per minute per user
- **Delete endpoints**: 5 requests per minute per user

---

## Caching Recommendations

Implement caching for improved performance:

- **Dashboard stats**: Cache for 5 minutes
- **Analytics data**: Cache for 10 minutes
- **Upcoming matches**: Cache for 1 hour
- **Rankings**: Cache for 5 minutes, invalidate on prediction changes
- **Client list**: Cache for 30 minutes

---

## Security Considerations

1. **Always validate and sanitize inputs** on the server side
2. **Use parameterized queries** to prevent SQL injection
3. **Hash passwords** using bcrypt or similar
4. **Use HTTPS** for all API communication
5. **Implement JWT token expiration** and refresh mechanism
6. **Validate token on every request** and check expiration
7. **Use CORS** properly to restrict API access
8. **Log security events** (failed logins, unauthorized access attempts)
9. **Implement rate limiting** to prevent brute force attacks
10. **Never expose sensitive data** in error messages
