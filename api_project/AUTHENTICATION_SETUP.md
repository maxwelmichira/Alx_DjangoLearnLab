# Authentication and Permissions Setup

## Overview
This API uses Token Authentication to secure endpoints. Only authenticated users can access and modify data.

## Authentication Configuration

### Settings
- **Authentication Class**: `TokenAuthentication`
- **Permission Class**: `IsAuthenticated` (applied to BookViewSet)

### How It Works
1. Users must obtain a token by providing valid credentials
2. The token must be included in the Authorization header for all API requests
3. Without a valid token, requests will receive a 401 Unauthorized response

## Obtaining a Token

**Endpoint**: `POST /api-token-auth/`

**Request**:
```bash
curl -X POST http://127.0.0.1:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

**Response**:
```json
{"token":"your_token_here"}
```

## Using the Token

Include the token in the Authorization header for all API requests:

**Header Format**: `Authorization: Token <your_token>`

**Example Request**:
```bash
curl -X GET http://127.0.0.1:8000/api/books_all/ \
  -H "Authorization: Token your_token_here"
```

## API Endpoints and Permissions

### BookViewSet (requires authentication)
- **GET /api/books_all/** - List all books (authenticated users only)
- **POST /api/books_all/** - Create a new book (authenticated users only)
- **GET /api/books_all/{id}/** - Retrieve a specific book (authenticated users only)
- **PUT /api/books_all/{id}/** - Update a book (authenticated users only)
- **DELETE /api/books_all/{id}/** - Delete a book (authenticated users only)

### BookList (no authentication required)
- **GET /api/books/** - List all books (public access)

## Testing

### Test without authentication:
```bash
curl -X GET http://127.0.0.1:8000/api/books_all/
# Expected: 401 Unauthorized
```

### Test with authentication:
```bash
# 1. Get token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"max","password":"your_password"}' | jq -r .token)

# 2. Use token to access API
curl -X GET http://127.0.0.1:8000/api/books_all/ \
  -H "Authorization: Token $TOKEN"
# Expected: 200 OK with list of books
```

## Security Notes
- Tokens are stored in the database and associated with user accounts
- Tokens do not expire by default
- Keep tokens secure and never share them publicly
- Use HTTPS in production to protect tokens in transit
