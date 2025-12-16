# User Profile and Preferences Endpoints

This document describes the user profile and preferences endpoints implemented in the Django backend.

## Endpoints

### 1. Get User Profile
**GET /api/users/profile**

Retrieves the authenticated user's profile including preferences.

**Authentication:** Required (session cookie)

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "display_name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "preferences": {
    "preferred_voice": "alloy",
    "preferred_language": "en",
    "favorite_topics": ["travel", "food"],
    "system_prompt_override": ""
  }
}
```

**Response (401 Unauthorized):** If not authenticated

---

### 2. Update User Profile
**PATCH /api/users/profile**

Updates the authenticated user's profile (display_name and/or email).

**Authentication:** Required (session cookie)

**Request Body:**
```json
{
  "display_name": "Jane Doe",
  "email": "newemail@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "newemail@example.com",
  "display_name": "Jane Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "preferences": {
    "preferred_voice": "alloy",
    "preferred_language": "en",
    "favorite_topics": ["travel", "food"],
    "system_prompt_override": ""
  }
}
```

**Response (400 Bad Request):** If email already exists or validation fails

**Response (401 Unauthorized):** If not authenticated

---

### 3. Update User Preferences
**PUT /api/users/preferences**

Updates the authenticated user's preferences. Creates UserPreferences if it doesn't exist.

**Authentication:** Required (session cookie)

**Request Body:**
```json
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"],
  "system_prompt_override": "You are a helpful travel assistant."
}
```

**Response (200 OK):**
```json
{
  "preferred_voice": "nova",
  "preferred_language": "es",
  "favorite_topics": ["travel", "technology"],
  "system_prompt_override": "You are a helpful travel assistant."
}
```

**Response (400 Bad Request):** If validation fails

**Response (401 Unauthorized):** If not authenticated

---

### 4. Change Password
**POST /api/users/change-password**

Changes the authenticated user's password after validating the current password.

**Authentication:** Required (session cookie)

**Request Body:**
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

**Response (400 Bad Request):** If current password is incorrect or new password doesn't meet requirements
```json
{
  "current_password": ["Current password is incorrect."]
}
```

**Response (401 Unauthorized):** If not authenticated

---

## Implementation Details

### Serializers
- `UserProfileSerializer`: Returns user profile with nested preferences
- `UserProfileUpdateSerializer`: Validates and updates display_name and email
- `UserPreferencesSerializer`: Handles user preferences CRUD
- `PasswordChangeSerializer`: Validates password change requests

### Views
- `profile_view`: Handles GET and PATCH for /api/users/profile
- `preferences_view`: Handles PUT for /api/users/preferences
- `change_password_view`: Handles POST for /api/users/change-password

### Security
- All endpoints require authentication via Django session cookie
- Email uniqueness is validated on profile updates
- Passwords are hashed using Django's default PBKDF2 hasher
- Current password must be validated before changing to new password
- Password strength validation enforces minimum 8 characters

### Requirements Satisfied
- Requirement 4.1: Profile retrieval with preferences
- Requirement 4.2: Profile update (display_name)
- Requirement 4.3: Profile update (email with validation)
- Requirement 4.4: Password change with current password validation
- Requirement 4.5: Password hashing and storage
- Requirement 5.1: Preferred voice storage
- Requirement 5.2: Preferred language storage
- Requirement 5.3: Favorite topics storage
