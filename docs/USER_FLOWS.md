# User Flow Diagrams

This document describes the various user flows in the Voice Agent system.

## Table of Contents

1. [Guest Mode Flow](#guest-mode-flow)
2. [Registration Flow](#registration-flow)
3. [Login Flow](#login-flow)
4. [Authenticated Session Flow](#authenticated-session-flow)
5. [Profile Management Flow](#profile-management-flow)
6. [History Viewing Flow](#history-viewing-flow)
7. [Logout Flow](#logout-flow)

---

## Guest Mode Flow

Users can use the voice agent without creating an account.

```
┌─────────────────────────────────────────────────────────────┐
│                     Guest Mode Flow                          │
└─────────────────────────────────────────────────────────────┘

User visits /chat
      │
      ▼
┌─────────────────┐
│  Chat Page      │
│  (Not logged in)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Options displayed:      │
│ - Continue as Guest     │
│ - Login                 │
│ - Sign Up               │
└────────┬────────────────┘
         │
         │ User clicks "Continue as Guest"
         ▼
┌─────────────────────────┐
│ Start Conversation      │
│ - Request mic permission│
│ - Connect to LiveKit    │
│ - Start agent session   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Voice Conversation      │
│ - Real-time transcripts │
│ - Agent responses       │
│ - No history saved      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ End Conversation        │
│ - Session not saved     │
│ - Can start new session │
└─────────────────────────┘
```

**Key Points**:
- No authentication required
- Session is not linked to any user
- Conversation is not saved to history
- User can convert to authenticated mode by logging in

---

## Registration Flow

New users create an account.

```
┌─────────────────────────────────────────────────────────────┐
│                   Registration Flow                          │
└─────────────────────────────────────────────────────────────┘

User visits /signup
      │
      ▼
┌─────────────────────────┐
│  Signup Page            │
│  - Email field          │
│  - Password field       │
│  - Confirm password     │
│  - Display name field   │
└────────┬────────────────┘
         │
         │ User fills form and submits
         ▼
┌─────────────────────────┐
│ Flask → Django          │
│ POST /api/auth/register │
└────────┬────────────────┘
         │
         ▼
    ┌────────┐
    │Validate│
    └───┬────┘
        │
        ├─── Valid ──────────────────┐
        │                            │
        │                            ▼
        │                   ┌─────────────────┐
        │                   │ Create User     │
        │                   │ Hash Password   │
        │                   │ Create Session  │
        │                   │ Set Cookie      │
        │                   └────────┬────────┘
        │                            │
        │                            ▼
        │                   ┌─────────────────┐
        │                   │ Return User Data│
        │                   └────────┬────────┘
        │                            │
        │                            ▼
        │                   ┌─────────────────┐
        │                   │ Redirect to     │
        │                   │ /chat           │
        │                   └─────────────────┘
        │
        └─── Invalid ───────────────┐
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Show Errors     │
                           │ - Email exists  │
                           │ - Weak password │
                           │ - Invalid format│
                           └─────────────────┘
```

**Validation Rules**:
- Email must be valid format and unique
- Password must be at least 8 characters
- Password cannot be too common
- Display name is required

**Success**:
- User account created
- Session cookie set
- Redirected to chat page
- User is now authenticated

---

## Login Flow

Existing users authenticate.

```
┌─────────────────────────────────────────────────────────────┐
│                      Login Flow                              │
└─────────────────────────────────────────────────────────────┘

User visits /login
      │
      ▼
┌─────────────────────────┐
│  Login Page             │
│  - Email field          │
│  - Password field       │
│  - "Continue as Guest"  │
│  - "Sign Up" link       │
└────────┬────────────────┘
         │
         │ User enters credentials and submits
         ▼
┌─────────────────────────┐
│ Flask → Django          │
│ POST /api/auth/login    │
└────────┬────────────────┘
         │
         ▼
    ┌────────────┐
    │Authenticate│
    └─────┬──────┘
          │
          ├─── Valid ──────────────────┐
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Create Session  │
          │                   │ Set Cookie      │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Return User Data│
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Redirect to     │
          │                   │ /chat           │
          │                   └─────────────────┘
          │
          └─── Invalid ───────────────┐
                                      │
                                      ▼
                             ┌─────────────────┐
                             │ Show Error      │
                             │ "Invalid        │
                             │  credentials"   │
                             └─────────────────┘
```

**Success**:
- Session cookie set
- Redirected to chat page
- User is now authenticated

**Failure**:
- Error message displayed
- User remains on login page
- Can retry or sign up

---

## Authenticated Session Flow

Authenticated users start voice conversations with preferences applied.

```
┌─────────────────────────────────────────────────────────────┐
│              Authenticated Session Flow                      │
└─────────────────────────────────────────────────────────────┘

User (logged in) visits /chat
      │
      ▼
┌─────────────────────────┐
│  Chat Page              │
│  Shows: "Welcome, John" │
│  - Profile link         │
│  - History link         │
│  - Logout link          │
└────────┬────────────────┘
         │
         │ User clicks "Start Conversation"
         ▼
┌─────────────────────────┐
│ Browser → FastAPI       │
│ GET /token              │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Connect to LiveKit      │
│ Publish microphone      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Browser → FastAPI       │
│ POST /session           │
│ (includes session cookie)│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ FastAPI → Django        │
│ POST /api/internal/     │
│   validate-session      │
└────────┬────────────────┘
         │
         ▼
    ┌────────────┐
    │  Valid?    │
    └─────┬──────┘
          │
          ├─── Yes ────────────────────┐
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Get User Data   │
          │                   │ Get Preferences │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Apply Preferences│
          │                   │ - Voice: nova   │
          │                   │ - Language: es  │
          │                   │ - Custom prompt │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Start Agent     │
          │                   │ Link to User    │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Voice Conversation│
          │                   │ - User preferences│
          │                   │ - Saved to history│
          │                   └─────────────────┘
          │
          └─── No ─────────────────────┐
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Anonymous Mode  │
                              │ (fallback)      │
                              └─────────────────┘
```

**Key Points**:
- Session cookie automatically sent with requests
- FastAPI validates session with Django
- User preferences automatically applied
- Session linked to user account
- Conversation saved to history

---

## Profile Management Flow

Users update their profile and preferences.

```
┌─────────────────────────────────────────────────────────────┐
│              Profile Management Flow                         │
└─────────────────────────────────────────────────────────────┘

User (logged in) visits /profile
      │
      ▼
┌─────────────────────────┐
│ Flask → Django          │
│ GET /api/users/profile  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Profile Page           │
│  - Email (read-only)    │
│  - Display name (edit)  │
│  - Created date         │
│  - Preferences section  │
│    • Voice selection    │
│    • Language selection │
│    • Favorite topics    │
│    • Custom prompt      │
│  - Change password link │
└────────┬────────────────┘
         │
         ├─── Update Profile ─────────┐
         │                            │
         │                            ▼
         │                   ┌─────────────────┐
         │                   │ User edits      │
         │                   │ display name    │
         │                   └────────┬────────┘
         │                            │
         │                            ▼
         │                   ┌─────────────────┐
         │                   │ Flask → Django  │
         │                   │ PATCH /api/users│
         │                   │   /profile      │
         │                   └────────┬────────┘
         │                            │
         │                            ▼
         │                   ┌─────────────────┐
         │                   │ Update Saved    │
         │                   │ Show Success    │
         │                   └─────────────────┘
         │
         └─── Update Preferences ────┐
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ User changes    │
                            │ - Voice: nova   │
                            │ - Language: es  │
                            └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Flask → Django  │
                   │ PUT /api/users/ │
                   │   preferences   │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Preferences Saved│
                   │ Applied to next │
                   │ conversation    │
                   └─────────────────┘
```

**Editable Fields**:
- Display name
- Preferred voice
- Preferred language
- Favorite topics
- Custom system prompt

**Password Change**:
- Requires current password
- New password must meet requirements
- Separate form/endpoint

---

## History Viewing Flow

Users view their past conversations.

```
┌─────────────────────────────────────────────────────────────┐
│               History Viewing Flow                           │
└─────────────────────────────────────────────────────────────┘

User (logged in) visits /history
      │
      ▼
┌─────────────────────────┐
│ Flask → Django          │
│ GET /api/auth/me        │
│ (check authentication)  │
└────────┬────────────────┘
         │
         ▼
    ┌────────────┐
    │Authenticated?│
    └─────┬──────┘
          │
          ├─── Yes ────────────────────┐
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Flask → Django  │
          │                   │ GET /api/users/ │
          │                   │   history       │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ History Page    │
          │                   │ - Session list  │
          │                   │ - Timestamps    │
          │                   │ - Message counts│
          │                   │ - Pagination    │
          │                   └────────┬────────┘
          │                            │
          │                            │ User clicks session
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Flask → Django  │
          │                   │ GET /api/users/ │
          │                   │   history/{id}  │
          │                   └────────┬────────┘
          │                            │
          │                            ▼
          │                   ┌─────────────────┐
          │                   │ Transcript Page │
          │                   │ - Full conversation│
          │                   │ - User messages │
          │                   │ - Agent messages│
          │                   │ - Timestamps    │
          │                   │ - Back link     │
          │                   └─────────────────┘
          │
          └─── No ─────────────────────┐
                                       │
                                       ▼
                              ┌─────────────────┐
                              │ Redirect to     │
                              │ /login          │
                              └─────────────────┘
```

**Features**:
- Paginated session list
- Most recent first
- Click to view full transcript
- User and agent messages distinguished
- Timestamps for each message

---

## Logout Flow

Users end their session.

```
┌─────────────────────────────────────────────────────────────┐
│                     Logout Flow                              │
└─────────────────────────────────────────────────────────────┘

User clicks "Logout" link
      │
      ▼
┌─────────────────────────┐
│ Flask → Django          │
│ POST /api/auth/logout   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Django Actions:         │
│ - Destroy session       │
│ - Clear session cookie  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Redirect to /           │
│ (home page)             │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ User is logged out      │
│ Can login again or      │
│ continue as guest       │
└─────────────────────────┘
```

**Effects**:
- Server-side session destroyed
- Session cookie cleared
- User must login again to access authenticated features
- Can still use guest mode

---

## System Architecture Flow

High-level view of how components interact.

```
┌─────────────────────────────────────────────────────────────┐
│                System Architecture Flow                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       ├─── HTTP/HTML ──────────────────┐
       │                                │
       │                                ▼
       │                       ┌─────────────────┐
       │                       │  Flask Frontend │
       │                       │  (Port 5173)    │
       │                       │  - Templates    │
       │                       │  - Static files │
       │                       │  - Routing      │
       │                       └────────┬────────┘
       │                                │
       │                                │ REST API
       │                                │ (session cookie)
       │                                │
       ├─── REST API ───────────────────┼────────┐
       │    (session cookie)            │        │
       │                                ▼        ▼
       │                       ┌─────────────────┐
       │                       │ Django Backend  │
       │                       │  (Port 9000)    │
       │                       │  - Auth         │
       │                       │  - Profiles     │
       │                       │  - History      │
       │                       │  - Persistence  │
       │                       └────────┬────────┘
       │                                │
       │                                │ Session
       │                                │ Validation
       │                                │
       ├─── REST API ───────────────────┼────────┐
       │    (LiveKit token)             │        │
       │                                │        │
       ├─── WebSocket ─────────────────┐│        │
       │    (transcripts)               ││        │
       │                                ││        │
       │                                ▼▼        ▼
       │                       ┌─────────────────┐
       │                       │ FastAPI Backend │
       │                       │  (Port 8000)    │
       │                       │  - Token mint   │
       │                       │  - Agent mgmt   │
       │                       │  - Transcripts  │
       │                       └────────┬────────┘
       │                                │
       │                                │ Agent
       │                                │ Connection
       │                                │
       └─── WebRTC ────────────────────┐│
            (audio)                    ││
                                       ▼▼
                              ┌─────────────────┐
                              │ LiveKit Server  │
                              │  - Media routing│
                              │  - Room mgmt    │
                              └─────────────────┘
```

**Data Flow**:
1. User interacts with Flask UI
2. Flask calls Django for auth/profile/history
3. Flask calls FastAPI for voice sessions
4. FastAPI validates sessions with Django
5. FastAPI manages LiveKit agent
6. Browser connects directly to LiveKit for audio
7. Transcripts flow: Agent → FastAPI → Browser (WebSocket)
8. Session data: FastAPI → Django (persistence)

---

## Error Handling Flows

### Authentication Failure

```
Login attempt
      │
      ▼
  Invalid credentials
      │
      ▼
┌─────────────────┐
│ Show error msg  │
│ Stay on login   │
│ Allow retry     │
└─────────────────┘
```

### Session Expiration

```
Authenticated request
      │
      ▼
  Session expired
      │
      ▼
┌─────────────────┐
│ Return 401      │
│ Redirect to     │
│ /login          │
└─────────────────┘
```

### Django Unreachable

```
FastAPI session start
      │
      ▼
  Django validation fails
      │
      ▼
┌─────────────────┐
│ Fallback to     │
│ anonymous mode  │
│ Continue session│
└─────────────────┘
```

### LiveKit Connection Failure

```
Browser connects to LiveKit
      │
      ▼
  Connection fails
      │
      ▼
┌─────────────────┐
│ Show error msg  │
│ Check LiveKit   │
│ URL and token   │
└─────────────────┘
```

---

## Best Practices

### For Users

1. **Create an account** to save conversation history
2. **Set preferences** before starting conversations
3. **Review history** to track past conversations
4. **Use guest mode** for quick, one-time conversations
5. **Logout** when using shared computers

### For Developers

1. **Handle session expiration** gracefully
2. **Validate all user input** on both client and server
3. **Use HTTPS** in production for secure cookies
4. **Implement proper CORS** configuration
5. **Log errors** for debugging
6. **Test all flows** thoroughly
7. **Provide clear error messages** to users
