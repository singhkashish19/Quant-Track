# API REFERENCE DOCUMENTATION

## Overview

QuantTrack API is a RESTful API built with FastAPI. All endpoints return JSON responses and require authentication (except auth endpoints).

### Base URL
```
http://localhost:8000/api  (development)
https://api.quanttrack.com (production)
```

### Authentication

All endpoints except `/auth/register` and `/auth/login` require a Bearer token:

```
Authorization: Bearer <access_token>
```

### Response Format

All responses follow this format:

```json
{
  "data": {...},
  "status": "success",
  "message": "Optional message"
}
```

Error responses:
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

---

## Authentication Endpoints

### Register User
```
POST /auth/register
```

**Request**
```json
{
  "email": "trader@example.com",
  "name": "John Trader",
  "password": "SecurePassword123!"
}
```

**Response** (201 Created)
```json
{
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "name": "John Trader",
    "is_active": true,
    "subscription_tier": "free"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

**Status Codes**
- 201: User created successfully
- 400: Invalid request or email already exists
- 500: Server error

---

### Login User
```
POST /auth/login
```

**Request**
```json
{
  "email": "trader@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK)
```json
{
  "user": {
    "id": 1,
    "email": "trader@example.com",
    "name": "John Trader",
    "is_active": true,
    "subscription_tier": "free"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

**Status Codes**
- 200: Login successful
- 401: Invalid credentials
- 500: Server error

---

### Refresh Token
```
POST /auth/refresh-token
```

**Request**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Verify Token
```
GET /auth/verify
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "id": 1,
  "email": "trader@example.com",
  "name": "John Trader",
  "is_active": true,
  "subscription_tier": "free"
}
```

---

## Trade Endpoints

### Create Trade
```
POST /trades
Authorization: Bearer <token>
```

**Request**
```json
{
  "symbol": "AAPL",
  "direction": "LONG",
  "entry_price": 150.25,
  "exit_price": 152.75,
  "stop_loss": 149.00,
  "take_profit": 155.00,
  "lot_size": 100,
  "strategy": "Breakout",
  "timeframe": "1H",
  "session": "NYSE",
  "emotional_state": "CONFIDENT",
  "entry_timestamp": "2024-01-15T09:30:00",
  "exit_timestamp": "2024-01-15T11:00:00",
  "notes": "Broke above resistance"
}
```

**Response** (201 Created)
```json
{
  "id": 42,
  "symbol": "AAPL",
  "direction": "LONG",
  "entry_price": 150.25,
  "exit_price": 152.75,
  "stop_loss": 149.00,
  "take_profit": 155.00,
  "lot_size": 100,
  "pnl": 250.0,
  "pnl_percentage": 1.67,
  "risk_reward_ratio": 2.5,
  "strategy": "Breakout",
  "timeframe": "1H",
  "session": "NYSE",
  "emotional_state": "CONFIDENT",
  "entry_timestamp": "2024-01-15T09:30:00",
  "exit_timestamp": "2024-01-15T11:00:00",
  "is_open": false,
  "notes": "Broke above resistance",
  "created_at": "2024-01-15T09:30:00",
  "updated_at": "2024-01-15T11:00:00"
}
```

---

### List Trades
```
GET /trades?skip=0&limit=50&symbol=AAPL&strategy=Breakout
Authorization: Bearer <token>
```

**Query Parameters**
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Page size (default: 50, max: 100)
- `symbol` (str): Filter by symbol (optional)
- `strategy` (str): Filter by strategy (optional)
- `session` (str): Filter by session (optional)

**Response** (200 OK)
```json
{
  "trades": [
    { ... trade object ... },
    { ... trade object ... }
  ],
  "total": 142,
  "page": 1,
  "page_size": 50,
  "total_pages": 3
}
```

---

### Get Single Trade
```
GET /trades/{trade_id}
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{ ... trade object ... }
```

---

### Update Trade
```
PUT /trades/{trade_id}
Authorization: Bearer <token>
```

**Request** (all fields optional)
```json
{
  "exit_price": 153.00,
  "notes": "Updated notes"
}
```

**Response** (200 OK)
```json
{ ... updated trade object ... }
```

---

### Delete Trade
```
DELETE /trades/{trade_id}
Authorization: Bearer <token>
```

**Response** (204 No Content)

---

### Get Trade Statistics
```
GET /trades/statistics/summary
Authorization: Bearer <token>
```

**Response** (200 OK)
```json
{
  "total_trades": 142,
  "winning_trades": 89,
  "losing_trades": 53,
  "win_rate": 62.7,
  "total_pnl": 15750.0,
  "average_pnl": 110.92,
  "largest_win": 1250.0,
  "largest_loss": -850.0,
  "open_trades": 3
}
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 204 | No Content - Successful deletion |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Server Error - Internal server error |

### Error Response Format
```json
{
  "detail": "Descriptive error message",
  "status_code": 400
}
```

---

## Rate Limiting

- Login endpoint: 5 requests per 5 minutes
- Other endpoints: 100 requests per minute

Headers in response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1674123456
```

---

## Examples Using cURL

### Register
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "name": "John Trader",
    "password": "SecurePassword123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecurePassword123!"
  }'
```

### Create Trade
```bash
curl -X POST http://localhost:8000/api/trades \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "direction": "LONG",
    "entry_price": 150.25,
    "lot_size": 100,
    "entry_timestamp": "2024-01-15T09:30:00"
  }'
```

---

## Interactive API Documentation

Visit `http://localhost:8000/api/docs` for interactive Swagger UI where you can:
- Explore all endpoints
- Test requests directly
- View response schemas
- See error examples

---

**API Documentation Last Updated**: May 2024
