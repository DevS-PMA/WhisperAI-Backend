# 🔐 Authentication API Endpoints
This project includes secure, asynchronous authentication routes built with FastAPI and MongoDB. Below is a detailed guide for the available auth routes.

## 📌 POST /auth/create
Description: Creates a new user account if the email is not already in use.

Request Body (JSON):

```json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "YourSecurePassword123"
}
```

### Behavior:

- Checks if the MongoDB database connection (userData) is initialized.

- Checks if the email is already registered.

- Hashes the password securely using passlib.

- Stores the user in the database.

- Returns a success message upon successful registration.

- Response (Success 200 OK):

```json

{
  "message": "Account john@example.com created successfully"
}
```

### Errors:

- 500 Internal Server Error: DB connection not initialized.

- 400 Bad Request: Email already in use.


## 📌 POST /auth/login
Description: Logs a user in by validating email and password and returns a JWT access token.

Request Body (JSON):

```json

{
  "email": "john@example.com",
  "password": "YourSecurePassword123"
}
```

### Behavior:

- Verifies database connection.

- Fetches the user by email from the database.

- Verifies the password using passlib.

- Serializes the user data and issues a JWT token with a 5-minute expiry.

- Returns user details and access token on successful login.

Response (Success 200 OK):

```json

{
  "user": {
    "email": "john@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "id": "6123abc..."
  },
  "token": "<JWT_TOKEN>",
  "token_type": "Bearer",
  "message": "Login to john@example.com successful"
}
```

### Errors:

- 500 Internal Server Error: DB connection not initialized.

- 400 Bad Request: Invalid email or password.


## 🔒 Security Notes
- Passwords are hashed using bcrypt via passlib.

- Tokens are generated using JWT with expiration.

- Responses do not expose password fields.

- Fails securely on invalid credentials.