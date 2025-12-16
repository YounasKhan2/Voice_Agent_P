# Implementation Plan: User Authentication and Profiles

- [x] 1. Set up Django user models and database schema
  - Create custom User model extending AbstractUser with email as username
  - Create UserPreferences model with one-to-one relationship to User
  - Add nullable foreign key from Session to User model
  - Create and run database migrations
  - Verify existing Session and Utterance data remains intact
  - _Requirements: 1.1, 1.3, 12.1, 12.2, 12.3, 12.5_

- [x] 2. Implement Django authentication endpoints
  - [x] 2.1 Create user serializers (UserSerializer, RegisterSerializer, LoginSerializer)
    - Write serializer for user registration with email, password, display_name validation
    - Write serializer for user profile responses
    - Add password strength validation (minimum 8 characters)
    - Add email format validation
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.2 Implement registration endpoint (POST /api/auth/register)
    - Create view that accepts email, password, display_name
    - Hash password using Django's password hasher
    - Create user account and UserPreferences record
    - Create Django session and set session cookie
    - Return user data (excluding password hash)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.3 Implement login endpoint (POST /api/auth/login)
    - Create view that accepts email and password
    - Authenticate user credentials
    - Create Django session on successful authentication
    - Set session cookie with HTTP-only and secure flags
    - Return user data on success, error on failure
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 2.4 Implement logout endpoint (POST /api/auth/logout)
    - Create view that destroys server-side session
    - Clear session cookie
    - Return success message
    - _Requirements: 10.4_

  - [x] 2.5 Implement current user endpoint (GET /api/auth/me)
    - Create view that returns authenticated user data
    - Return 401 if not authenticated
    - Include user ID, email, display_name
    - _Requirements: 10.3_

  - [x] 2.6 Configure Django session and CORS settings
    - Set SESSION_COOKIE_HTTPONLY=True
    - Set SESSION_COOKIE_SECURE=True in production
    - Set SESSION_COOKIE_SAMESITE='Lax'
    - Configure CORS to allow Flask frontend origin with credentials
    - Set SESSION_COOKIE_AGE to 14 days
    - _Requirements: 11.1, 11.2, 11.3, 11.5_

- [x] 3. Implement user profile and preferences endpoints
  - [x] 3.1 Create profile retrieval endpoint (GET /api/users/profile)
    - Require authentication via session cookie
    - Return user profile with email, display_name, created_at
    - Include user preferences (voice, language, topics)
    - Return 401 if not authenticated
    - _Requirements: 4.1_

  - [x] 3.2 Create profile update endpoint (PATCH /api/users/profile)
    - Require authentication via session cookie
    - Allow updating display_name and email
    - Validate email uniqueness and format
    - Return updated profile data
    - _Requirements: 4.2, 4.3_

  - [x] 3.3 Create preferences update endpoint (PUT /api/users/preferences)
    - Require authentication via session cookie
    - Accept preferred_voice, preferred_language, favorite_topics
    - Create UserPreferences if doesn't exist
    - Update and return preferences
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 3.4 Create password change endpoint (POST /api/users/change-password)
    - Require authentication via session cookie
    - Validate current password
    - Hash and store new password
    - Return success message
    - _Requirements: 4.4, 4.5_

- [x] 4. Implement conversation history endpoints
  - [x] 4.1 Create history list endpoint (GET /api/users/history)
    - Require authentication via session cookie
    - Query sessions filtered by user foreign key
    - Order by started_at descending
    - Include pagination (limit, offset)
    - Return session metadata with utterance count
    - _Requirements: 7.1, 7.4, 7.5_

  - [x] 4.2 Create session detail endpoint (GET /api/users/history/{session_id})
    - Require authentication via session cookie
    - Verify session belongs to authenticated user
    - Return session metadata and all utterances
    - Return 404 if session not found or doesn't belong to user
    - Order utterances by created_at
    - _Requirements: 7.2, 7.3_

- [x] 5. Create internal session validation endpoint for FastAPI
  - Create endpoint POST /api/internal/validate-session
  - Accept session cookie in request
  - Check if user is authenticated
  - Return user_id, email, display_name, and preferences if valid
  - Return 401 if session invalid
  - Do not expose this endpoint publicly (internal use only)
  - _Requirements: 6.2_

- [x] 6. Enhance FastAPI backend for authenticated sessions
  - [x] 6.1 Create session validation utility
    - Write async function to call Django's validate-session endpoint
    - Accept session cookie string as parameter
    - Return user data dict if valid, None if invalid
    - Handle network errors gracefully (return None)
    - Add timeout of 5 seconds
    - _Requirements: 6.2_

  - [x] 6.2 Enhance session start endpoint to support authentication
    - Modify POST /session to accept optional session cookie
    - Call session validation utility if cookie present
    - Extract user_id and preferences from validation response
    - Apply user's preferred_voice to TTS engine if available
    - Apply user's system_prompt_override if available
    - Include user_id in session metadata for persistence
    - Maintain backward compatibility (work without cookie)
    - _Requirements: 6.1, 6.2, 6.3, 6.5, 1.1, 1.2_

  - [x] 6.3 Update AgentManager to accept user context
    - Add optional user_id parameter to start_session method
    - Add optional user_preferences parameter to start_session method
    - Apply preferred_voice from preferences to TTS engine
    - Apply preferred_language from preferences if supported
    - Include user_id in session metadata sent to Django persistence
    - Maintain backward compatibility (work with None values)
    - _Requirements: 5.4, 5.5, 6.3_

- [x] 7. Create Flask authentication UI pages
  - [x] 7.1 Create login page template and route
    - Create templates/login.html with email and password fields
    - Add form submission that POSTs to Django /api/auth/login
    - Display error messages from Django API
    - Add link to signup page
    - Add "Continue as guest" link to chat page
    - Create Flask route /login that renders template
    - Handle POST request by forwarding to Django API
    - Redirect to chat page on successful login
    - _Requirements: 9.1, 9.3, 10.1_

  - [x] 7.2 Create signup page template and route
    - Create templates/signup.html with email, password, confirm password, display_name fields
    - Add client-side password confirmation validation
    - Add form submission that POSTs to Django /api/auth/register
    - Display validation errors from Django API
    - Add link to login page
    - Create Flask route /signup that renders template
    - Handle POST request by forwarding to Django API
    - Redirect to chat page on successful registration
    - _Requirements: 9.2, 9.4_

  - [x] 7.3 Create logout route
    - Create Flask route /logout
    - Call Django /api/auth/logout endpoint
    - Redirect to home page
    - _Requirements: 10.4_

  - [x] 7.4 Enhance chat page to show user status
    - Modify templates/chat.html to include user info bar
    - Check authentication status by calling Django /api/auth/me
    - Display "Welcome, {display_name}" if authenticated
    - Display "Guest Mode" if not authenticated
    - Add links to Profile, History, Logout for authenticated users
    - Add links to Login, Sign Up for guest users
    - Pass user data to JavaScript via window.APP_CONFIG
    - Maintain existing chat functionality unchanged
    - _Requirements: 10.1, 10.2, 10.3, 1.1_

- [x] 8. Create Flask history UI pages
  - [x] 8.1 Create history list page
    - Create templates/history.html to display session list
    - Create Flask route /history
    - Check authentication by calling Django /api/auth/me
    - Redirect to login if not authenticated
    - Fetch user's sessions from Django /api/users/history
    - Display sessions with timestamps, room names, message counts
    - Add link to view each session's transcript
    - Show empty state if no history
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 8.2 Create session detail page
    - Create templates/history_detail.html to display full transcript
    - Create Flask route /history/<session_id>
    - Fetch session details from Django /api/users/history/{session_id}
    - Display conversation with user and agent messages clearly distinguished
    - Handle 404 if session not found or doesn't belong to user
    - Add back link to history list
    - _Requirements: 8.2, 8.4, 8.5_

- [x] 9. Create Flask profile page
  - Create templates/profile.html to display and edit user info
  - Create Flask route /profile
  - Check authentication and redirect to login if needed
  - Fetch user profile from Django /api/users/profile
  - Display email, display_name, created_at
  - Add form to update display_name
  - Add form to update preferences (voice, language, topics)
  - Handle form submissions by calling Django API endpoints
  - Display success/error messages
  - _Requirements: 4.1, 4.2, 5.1, 5.2, 5.3_

- [x] 10. Add CSS styling for new pages
  - Create or update static/css/style.css
  - Style authentication forms (login, signup)
  - Style user info bar on chat page
  - Style history list and session cards
  - Style profile page and forms
  - Ensure responsive design for mobile devices
  - Match existing chat page styling

- [x] 11. Update environment configuration
  - Add DJANGO_API_URL to flask_frontend/.env
  
  - Add SESSION_COOKIE_AGE to django_persistence/.env
  - Add SESSION_COOKIE_SECURE to django_persistence/.env
  - Add CORS_ALLOWED_ORIGINS to django_persistence/.env
  - Update Backend/.env to include DJANGO_BASE_URL for session validation
  - Document new environment variables in README

- [x] 12. Create database migration scripts
  - Generate Django migration for User model
  - Generate Django migration for UserPreferences model
  - Generate Django migration to add User foreign key to Session
  - Test migrations on clean database
  - Test migrations on database with existing sessions
  - Verify existing data remains intact after migrations
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 13. Integration testing and verification
  - [x] 13.1 Test anonymous session flow (existing behavior)
    - Start chat as guest without logging in
    - Verify session starts successfully
    - Verify transcripts stream correctly
    - Verify session is stored with null user_id
    - Confirm no breaking changes to existing functionality
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 13.2 Test registration and login flow
    - Register new user with valid data
    - Verify session cookie is set
    - Verify redirect to chat page
    - Logout and verify session cleared
    - Login with same credentials
    - Verify session cookie is set again
    - _Requirements: 2.1, 2.5, 3.1, 3.5, 10.4_

  - [x] 13.3 Test authenticated session flow
    - Login as registered user
    - Start voice conversation
    - Verify session is linked to user_id
    - Verify transcripts are saved
    - Check history page shows the session
    - Verify session detail displays correct transcript
    - _Requirements: 6.1, 6.2, 6.3, 7.1, 7.2_

  - [x] 13.4 Test user preferences application
    - Login as user
    - Set preferred voice to "nova"
    - Set preferred language to "es"
    - Start new conversation
    - Verify agent uses "nova" voice
    - Check session metadata includes preferences
    - _Requirements: 5.1, 5.2, 5.4, 5.5_

  - [x] 13.5 Test error handling and edge cases
    - Test login with invalid credentials
    - Test registration with existing email
    - Test accessing history without authentication
    - Test session validation with expired cookie
    - Test FastAPI fallback when Django is unreachable
    - Verify graceful degradation to anonymous mode
    - _Requirements: 3.2, 2.2, 8.3, 6.4_

- [x] 14. Update documentation
  - Update README.md with authentication features
  - Document new API endpoints in docs/
  - Add setup instructions for new environment variables
  - Document user flow diagrams
  - Add troubleshooting section for common issues
  - Update project roadmap to mark completed features
