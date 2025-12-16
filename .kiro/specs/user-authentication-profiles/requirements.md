# Requirements Document: User Authentication and Profiles

## Introduction

This document specifies the addition of user authentication, profiles, preferences, and conversation history features to the existing Voice Agent system. The implementation must maintain full backward compatibility with the current anonymous session functionality, ensuring that existing features continue to work without modification.

## Glossary

- **Voice Agent System**: The existing real-time voice conversation application using FastAPI, Flask, LiveKit, and Django persistence
- **Anonymous Session**: A voice conversation session created without user authentication (current behavior)
- **Authenticated Session**: A voice conversation session linked to a registered user account
- **User Profile**: A registered user account containing identity information and preferences
- **User Preferences**: Configurable settings for voice, language, and conversation topics
- **Conversation History**: A collection of past sessions and their transcripts associated with a user
- **Django Backend**: The persistence service that stores sessions, utterances, and will store user data
- **Flask Frontend**: The web UI that serves HTML pages for user interaction
- **FastAPI Backend**: The service that orchestrates LiveKit agent sessions
- **Session Cookie**: HTTP-only cookie used for authenticating API requests via Django session framework

## Requirements

### Requirement 1: Backward Compatibility

**User Story:** As an existing user, I want to continue using the voice agent without creating an account, so that I can have quick anonymous conversations as before.

#### Acceptance Criteria

1. WHEN a user visits the chat page without authentication, THE Voice Agent System SHALL allow them to start anonymous sessions exactly as the current system operates
2. WHEN an anonymous session is created, THE Voice Agent System SHALL NOT require any user credentials or authentication tokens
3. WHEN the system processes an anonymous session, THE Django Backend SHALL store the session with a null user_id field
4. THE Voice Agent System SHALL maintain all existing API endpoints with their current request and response formats
5. THE Voice Agent System SHALL preserve the current session lifecycle (token minting, session start, WebSocket transcripts, session stop) for anonymous users

### Requirement 2: User Registration

**User Story:** As a new user, I want to create an account with email and password, so that I can save my conversation history and preferences.

#### Acceptance Criteria

1. WHEN a user submits valid registration data (email, password, display name), THE Django Backend SHALL create a new user account with hashed password storage
2. WHEN a user attempts to register with an existing email, THE Django Backend SHALL return an error indicating the email is already registered
3. WHEN a user provides a password shorter than 8 characters, THE Django Backend SHALL reject the registration with a validation error
4. THE Django Backend SHALL validate email format before creating an account
5. WHEN registration succeeds, THE Django Backend SHALL create an authenticated session and return a session cookie

### Requirement 3: User Login

**User Story:** As a registered user, I want to log in with my email and password, so that I can access my personalized features and history.

#### Acceptance Criteria

1. WHEN a user submits valid credentials (email and password), THE Django Backend SHALL authenticate the user and create a server-side session
2. WHEN a user submits invalid credentials, THE Django Backend SHALL return an authentication error without revealing whether the email exists
3. WHEN a session is created, THE Django Backend SHALL store the user ID in the server-side session data
4. THE Django Backend SHALL set session cookie as HTTP-only and secure in production environments
5. WHEN a user logs in successfully, THE Django Backend SHALL return a session cookie that the browser automatically stores

### Requirement 4: User Profile Management

**User Story:** As a registered user, I want to view and update my profile information, so that I can keep my account details current.

#### Acceptance Criteria

1. WHEN an authenticated user requests their profile, THE Django Backend SHALL return the user's email, display name, and account creation date
2. WHEN an authenticated user updates their display name, THE Django Backend SHALL save the new name and return the updated profile
3. WHEN an authenticated user updates their email, THE Django Backend SHALL validate the new email format and uniqueness before saving
4. WHEN an authenticated user requests a password change with valid current password, THE Django Backend SHALL hash and store the new password
5. THE Django Backend SHALL NOT return password hashes in any API response

### Requirement 5: User Preferences

**User Story:** As a registered user, I want to set my preferred voice, language, and conversation topics, so that the agent personalizes conversations to my preferences.

#### Acceptance Criteria

1. WHEN an authenticated user sets a preferred TTS voice, THE Django Backend SHALL store the voice identifier in the user preferences
2. WHEN an authenticated user sets a preferred language, THE Django Backend SHALL store the language code in the user preferences
3. WHEN an authenticated user sets favorite topics, THE Django Backend SHALL store the topics as a JSON array in the user preferences
4. WHEN an authenticated user starts a session, THE FastAPI Backend SHALL retrieve the user's preferences and apply them to the agent configuration
5. WHERE a user has not set preferences, THE Voice Agent System SHALL use the default system configuration

### Requirement 6: Authenticated Sessions

**User Story:** As a registered user, I want my voice conversations to be linked to my account, so that I can review them later in my history.

#### Acceptance Criteria

1. WHEN an authenticated user starts a session, THE Flask Frontend SHALL include the session cookie in the session start request
2. WHEN the FastAPI Backend receives a session start request with a valid session cookie, THE FastAPI Backend SHALL validate the session with Django and extract the user ID to include in the session metadata
3. WHEN the Django Backend stores a session with user metadata, THE Django Backend SHALL link the session to the user account via the user_id foreign key
4. WHEN an authenticated user's session cookie is invalid or expired, THE FastAPI Backend SHALL reject the session start request with an authentication error
5. WHERE an authenticated user's session is created, THE Voice Agent System SHALL maintain all existing real-time transcript and audio functionality

### Requirement 7: Conversation History Retrieval

**User Story:** As a registered user, I want to view a list of my past conversations, so that I can review what I discussed with the agent.

#### Acceptance Criteria

1. WHEN an authenticated user requests their conversation history, THE Django Backend SHALL return all sessions linked to their user ID ordered by most recent first
2. WHEN an authenticated user requests a specific session detail, THE Django Backend SHALL return the session metadata and all associated utterances
3. WHEN an authenticated user requests history, THE Django Backend SHALL NOT return sessions belonging to other users
4. THE Django Backend SHALL include session start time, end time, room name, and utterance count in the history list
5. WHERE a user has no conversation history, THE Django Backend SHALL return an empty list

### Requirement 8: History UI Page

**User Story:** As a registered user, I want to access a history page in the web interface, so that I can browse and read my past conversations.

#### Acceptance Criteria

1. WHEN an authenticated user navigates to the history page, THE Flask Frontend SHALL display a list of their past sessions with timestamps
2. WHEN an authenticated user clicks on a session in the history list, THE Flask Frontend SHALL display the full conversation transcript
3. WHEN an unauthenticated user attempts to access the history page, THE Flask Frontend SHALL redirect them to the login page
4. THE Flask Frontend SHALL display user and agent messages in a readable conversation format
5. THE Flask Frontend SHALL indicate which messages are from the user and which are from the agent

### Requirement 9: Authentication UI

**User Story:** As a user, I want clear login and signup pages in the web interface, so that I can easily create an account or sign in.

#### Acceptance Criteria

1. WHEN a user navigates to the login page, THE Flask Frontend SHALL display email and password input fields with a submit button
2. WHEN a user navigates to the signup page, THE Flask Frontend SHALL display email, password, confirm password, and display name fields with a submit button
3. WHEN a user submits the login form with valid credentials, THE Flask Frontend SHALL receive a session cookie and redirect to the chat page
4. WHEN a user submits the signup form successfully, THE Flask Frontend SHALL receive a session cookie and redirect to the chat page
5. THE Flask Frontend SHALL display validation errors returned from the Django Backend in a user-friendly format

### Requirement 10: Optional Authentication

**User Story:** As a user, I want the option to use the voice agent with or without logging in, so that I have flexibility in how I use the application.

#### Acceptance Criteria

1. WHEN a user visits the chat page, THE Flask Frontend SHALL display both "Continue as Guest" and "Login" options
2. WHEN a user selects "Continue as Guest", THE Voice Agent System SHALL create an anonymous session using the existing flow
3. WHEN an authenticated user visits the chat page, THE Flask Frontend SHALL display their display name and a logout option
4. WHEN an authenticated user logs out, THE Django Backend SHALL destroy the server-side session and clear the session cookie
5. THE Flask Frontend SHALL NOT require authentication to access the main chat functionality

### Requirement 11: Security

**User Story:** As a system administrator, I want user passwords securely hashed and API endpoints protected, so that user data remains secure.

#### Acceptance Criteria

1. WHEN a user password is stored, THE Django Backend SHALL hash the password using Django's default password hasher (PBKDF2)
2. WHEN an API endpoint requires authentication, THE Django Backend SHALL validate the session cookie and verify the session exists in the session store
3. WHEN a session cookie is expired or invalid, THE Django Backend SHALL reject the request with a 401 Unauthorized status
4. THE Django Backend SHALL NOT log or expose password hashes in any API response or log output
5. THE Django Backend SHALL set session cookies with HTTP-only and SameSite flags to prevent XSS and CSRF attacks

### Requirement 12: Database Schema Extensions

**User Story:** As a developer, I want new database models that extend the existing schema without breaking current functionality, so that the system remains stable during the upgrade.

#### Acceptance Criteria

1. THE Django Backend SHALL create a User model with fields for email, password hash, display name, and creation timestamp
2. THE Django Backend SHALL create a UserPreferences model with fields for preferred voice, language, and topics linked to the User model
3. THE Django Backend SHALL maintain the existing Session model structure with the user_id field remaining nullable
4. THE Django Backend SHALL maintain the existing Utterance model structure without modifications
5. WHEN database migrations are applied, THE Django Backend SHALL NOT modify or delete existing session or utterance data

## Non-Functional Requirements

### Performance
- Authentication endpoints SHALL respond within 500 milliseconds under normal load
- History retrieval for 100 sessions SHALL complete within 2 seconds
- Session validation SHALL add no more than 50 milliseconds to request processing time

### Security
- Passwords SHALL be hashed using PBKDF2 with at least 100,000 iterations
- Session cookies SHALL be set with HTTP-only, Secure, and SameSite=Lax flags
- API endpoints SHALL use HTTPS in production environments
- CORS configuration SHALL restrict origins to authorized domains in production

### Scalability
- The system SHALL support at least 1,000 registered users without performance degradation
- History queries SHALL use database indexes on user_id and created_at fields
- Session validation SHALL use Django's session framework with database or cache backend

### Usability
- Login and signup forms SHALL provide clear error messages for validation failures
- The history page SHALL load and display within 3 seconds for users with up to 50 sessions
- Authentication state SHALL persist across browser sessions until token expiration or logout

### Compatibility
- All existing API endpoints SHALL maintain their current request and response formats
- Anonymous sessions SHALL continue to function identically to the current implementation
- The system SHALL support the same browsers as the current implementation (Chrome, Edge, Firefox, Safari)

## External Dependencies

- Django REST Framework (for API endpoints)
- Django authentication system (for password hashing and session management)
- Django session framework (for server-side session storage)
- Existing dependencies: FastAPI, Flask, LiveKit, OpenAI

## Environment Variables

New environment variables to be added:

- `SESSION_COOKIE_AGE`: Number of seconds before session expires (default: 1209600, which is 14 days)
- `SESSION_COOKIE_SECURE`: Whether to use secure cookies (default: true in production)
- `SESSION_COOKIE_HTTPONLY`: Whether cookies are HTTP-only (default: true)
- `SESSION_COOKIE_SAMESITE`: SameSite cookie attribute (default: 'Lax')
- `REQUIRE_EMAIL_VERIFICATION`: Whether to require email verification for new accounts (default: false)

Existing environment variables remain unchanged.

## Acceptance Tests (High-level)

### Anonymous User Flow (Existing Functionality)
- User visits chat page without logging in
- User starts conversation as guest
- Conversation works identically to current system
- Session is stored with null user_id

### Registration and Login Flow
- User navigates to signup page
- User creates account with email and password
- User receives session cookie and is redirected to chat
- User can log out and log back in with same credentials

### Authenticated Session Flow
- Logged-in user starts conversation
- Session is linked to user account
- User can view session in history page
- Transcript is displayed correctly

### Preferences Flow
- Logged-in user sets preferred voice and language
- User starts new conversation
- Agent uses user's preferred settings
- Conversation reflects personalized configuration

### History Flow
- Logged-in user navigates to history page
- User sees list of past conversations
- User clicks on a conversation
- Full transcript is displayed with correct formatting
