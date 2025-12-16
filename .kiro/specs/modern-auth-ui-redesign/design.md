# Design Document

## Overview

This design document outlines the implementation of the VoyageAI brand design from Stitch, featuring a travel-themed authentication UI with Tailwind CSS, Material Symbols icons, and Plus Jakarta Sans typography. The design removes guest mode, introduces a VoyageAI branded landing dashboard, and implements split-screen authentication pages with smooth animations. The design focuses on creating a polished, travel-focused user experience while maintaining proper integration with the existing Django backend for user management.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Frontend Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Landing Dashboard  │  Login Page  │  Signup Page           │
│  (New)              │  (Redesigned)│  (Redesigned)          │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ HTTP/REST API
               │
┌──────────────▼──────────────────────────────────────────────┐
│                   Django Backend Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Authentication  │  User Model  │  Django Admin             │
│  Views           │  Management  │  Configuration            │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Landing Dashboard Flow**:
   - User visits root URL → Redirected to landing dashboard
   - Landing dashboard displays branding + auth buttons
   - No guest mode option available

2. **Authentication Flow**:
   - User clicks login/signup → Navigate to respective page with animation
   - Form submission → Django API validation
   - Success → Toast notification (signup) → Redirect to chat dashboard
   - Failure → Display error message inline

3. **Session Management**:
   - Django session cookies maintain authentication state
   - Flask passes cookies to Django for validation
   - Authenticated users access full application features

## Components and Interfaces

### 1. Landing Dashboard Component (VoyageAI Welcome Screen)

**File**: `flask_frontend/templates/landing.html`

**Purpose**: Serve as the initial entry point for unauthenticated users with VoyageAI travel theme

**Structure**:
```html
<div class="bg-background-light dark:bg-background-dark">
  <!-- Header with Logo and Navigation -->
  <header class="border-b border-gray-200 dark:border-[#233648]">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <span class="material-symbols-outlined text-primary">travel_explore</span>
        <h2 class="text-lg font-bold">VoyageAI</h2>
      </div>
      <nav>
        <a href="/login">Sign In</a>
        <a href="#">My Trips</a>
      </nav>
    </div>
  </header>
  
  <!-- Hero Section with Gradient Background -->
  <div class="hero-section bg-gradient">
    <h1>Hello, I'm your travel AI assistant.</h1>
    <p>Your personal guide to seamless travel planning.</p>
    <div class="search-bar">
      <input placeholder="Plan a trip to Tokyo..." />
      <button class="bg-primary">Send</button>
    </div>
  </div>
  
  <!-- Features Section -->
  <div class="features-section">
    <h2>How I can help</h2>
    <div class="feature-cards grid">
      <div class="feature-card">
        <span class="material-symbols-outlined">flight</span>
        <h3>Find Flights</h3>
        <p>Get the best real-time deals on flights across all airlines.</p>
      </div>
      <div class="feature-card">
        <span class="material-symbols-outlined">hotel</span>
        <h3>Book Hotels</h3>
        <p>Discover and book the perfect stay for your trip.</p>
      </div>
      <div class="feature-card">
        <span class="material-symbols-outlined">description</span>
        <h3>Create Itineraries</h3>
        <p>Let me build a personalized day-by-day plan for you.</p>
      </div>
    </div>
  </div>
  
  <!-- Footer -->
  <footer class="border-t border-gray-200 dark:border-[#233648]">
    <nav>
      <a href="#">About</a>
      <a href="#">Privacy Policy</a>
      <a href="#">Terms of Service</a>
    </nav>
    <div class="social-icons">
      <!-- Twitter, Instagram, Facebook icons -->
    </div>
    <p>© 2024 VoyageAI. All rights reserved.</p>
  </footer>
</div>
```

**Styling Approach**:
- Tailwind CSS utility classes for all styling
- Dark theme with background-dark (#101922)
- Plus Jakarta Sans font family
- Material Symbols icons
- Primary color #137fec for CTAs
- Gradient background for hero section
- Responsive grid layout for feature cards

### 2. Split-Screen Login Page (VoyageAI Login)

**File**: `flask_frontend/templates/login.html`

**Layout Structure**:
```
┌─────────────────────────────────────┐
│  Left Side (50%)  │  Right Side (50%)│
│                   │                  │
│  Branding Panel   │  Login Form      │
│  - World map bg   │  - Welcome Back  │
│  - VoyageAI logo  │  - Email input   │
│  - "Your journey, │  - Password      │
│    reimagined"    │  - Visibility    │
│  - Description    │  - Log In btn    │
│  - Dark overlay   │  - Google OAuth  │
│                   │  - Sign up link  │
└─────────────────────────────────────┘
```

**Left Branding Panel**:
```html
<div class="bg-[#1A202C] relative">
  <!-- World map background with opacity-10 -->
  <div class="absolute inset-0 bg-cover opacity-10" style="background-image: url(...)"></div>
  
  <div class="relative z-10 text-center">
    <div class="flex items-center gap-4">
      <span class="material-symbols-outlined text-4xl text-primary">travel_explore</span>
      <span class="text-3xl font-bold text-white">VoyageAI</span>
    </div>
    <h1 class="text-4xl font-bold text-white">Your journey, reimagined.</h1>
    <p class="text-lg text-gray-300">Intelligent travel planning starts here...</p>
  </div>
</div>
```

**Right Form Panel**:
```html
<div class="bg-background-light dark:bg-background-dark">
  <div class="max-w-md">
    <h1 class="text-3xl font-bold">Welcome Back</h1>
    <h2 class="text-base text-slate-600 dark:text-slate-400">Log in to your account to continue.</h2>
    
    <form>
      <label>
        <p class="text-sm font-medium">Email Address</p>
        <input class="form-input h-12 rounded-lg border border-slate-300 dark:border-slate-700" />
      </label>
      
      <div>
        <div class="flex justify-between">
          <p class="text-sm font-medium">Password</p>
          <a class="text-sm text-primary">Forgot password?</a>
        </div>
        <div class="flex items-stretch">
          <input type="password" class="form-input rounded-l-lg border-r-0" />
          <div class="rounded-r-lg border border-l-0">
            <span class="material-symbols-outlined">visibility</span>
          </div>
        </div>
      </div>
      
      <button class="h-12 bg-primary text-white rounded-lg">Log In</button>
    </form>
    
    <p class="text-center">Don't have an account? <a class="text-primary">Sign up</a></p>
  </div>
</div>
```

**Key Design Elements**:
- Tailwind CSS utility classes
- Material Symbols for icons
- Primary color #137fec
- Dark theme backgrounds
- Plus Jakarta Sans font
- World map background image
- Password visibility toggle
- Google OAuth button with logo

### 3. Split-Screen Signup Page (VoyageAI Signup)

**File**: `flask_frontend/templates/signup.html`

**Layout Structure**:
```
┌─────────────────────────────────────┐
│  Left Side (50%)  │  Right Side (50%)│
│                   │                  │
│  Signup Form      │  Branding Panel  │
│  - Begin Your     │  - Globe bg      │
│    Next Adventure │  - VoyageAI logo │
│  - Google OAuth   │  - "Your personal│
│  - Apple OAuth    │    travel        │
│  - Email input    │    architect"    │
│  - Password       │  - 3 Value Props │
│  - Strength bar   │  - Icons         │
│  - Create Account │                  │
│  - Login link     │                  │
└─────────────────────────────────────┘
```

**Left Form Panel**:
```html
<div class="bg-background-light dark:bg-background-dark">
  <div class="max-w-md">
    <h1 class="text-4xl font-black">Begin Your Next Adventure</h1>
    <p class="text-base text-slate-500 dark:text-slate-400">Join 10,000+ happy travelers...</p>
    
    <form>
      <label>
        <p class="text-base font-medium">Email</p>
        <input class="form-input h-14 rounded-lg border border-slate-300 dark:border-slate-700" />
      </label>
      
      <label>
        <p class="text-base font-medium">Password</p>
        <div class="relative">
          <input type="password" class="form-input h-14 rounded-lg pr-12" />
          <div class="absolute right-0 inset-y-0 flex items-center pr-4">
            <span class="material-symbols-outlined">visibility</span>
          </div>
        </div>
      </label>
      
      <!-- Password Strength Indicator -->
      <div class="flex items-center gap-2">
        <div class="h-1 flex-1 rounded-full bg-slate-200 dark:bg-slate-700">
          <div class="h-1 w-1/3 rounded-full bg-red-500"></div>
        </div>
        <p class="text-sm text-slate-500">Weak</p>
      </div>
      
      <button class="mt-4 h-12 bg-primary text-white rounded-lg">Create Free Account</button>
    </form>
    
    <p class="text-center text-sm">Already have an account? <a class="text-primary">Log in</a></p>
  </div>
</div>
```

**Right Branding Panel**:
```html
<div class="bg-slate-900 relative">
  <!-- Globe background with opacity-10 -->
  <img class="absolute inset-0 opacity-10" src="..." />
  <div class="absolute inset-0 bg-gradient-to-t from-background-dark"></div>
  
  <div class="relative z-10">
    <div class="flex items-center gap-3">
      <div class="h-12 w-12 rounded-xl bg-primary/20 text-primary">
        <span class="material-symbols-outlined text-3xl">travel_explore</span>
      </div>
      <p class="text-2xl font-bold text-white">VoyagerAI</p>
    </div>
    <p class="text-4xl font-black text-white">Your personal travel architect.</p>
    
    <!-- Value Propositions -->
    <div class="flex flex-col gap-6">
      <div class="flex items-start gap-4">
        <div class="h-8 w-8 rounded-full bg-primary/20 text-primary">
          <span class="material-symbols-outlined">route</span>
        </div>
        <div>
          <p class="font-bold text-white">Personalized Itineraries</p>
          <p class="text-slate-400">Crafted just for you...</p>
        </div>
      </div>
      <!-- Repeat for 24/7 AI Assistance and Discover Hidden Gems -->
    </div>
  </div>
</div>
```

**Key Design Elements**:
- Tailwind CSS utility classes
- Material Symbols for icons
- Primary color #137fec
- Password strength indicator (red/weak)
- Google and Apple OAuth buttons
- Globe background image
- Three value proposition cards with icons
- Plus Jakarta Sans font

### 4. Toast Notification Component

**Implementation**: JavaScript-based toast system

**Structure**:
```javascript
class ToastNotification {
  show(message, type, duration) {
    // Create toast element
    // Animate in
    // Auto-dismiss after duration
    // Animate out
  }
}
```

**Toast Types**:
- Success (green) - Registration successful
- Error (red) - Validation errors
- Info (blue) - General information
- Warning (yellow) - Warnings

**Behavior**:
- Slide in from top-right
- Display for 3-5 seconds
- Fade out animation
- Dismissible by clicking X button
- Stack multiple toasts vertically

### 5. Page Transition Animation System

**Implementation**: CSS transitions + JavaScript navigation

**Animation Types**:

1. **Fade Transition**:
```css
.page-transition-fade {
  animation: fadeOut 0.3s ease-out;
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
```

2. **Slide Transition**:
```css
.page-transition-slide {
  animation: slideOut 0.4s ease-in-out;
}

@keyframes slideOut {
  from { transform: translateX(0); }
  to { transform: translateX(-100%); }
}
```

**JavaScript Controller**:
```javascript
function navigateWithAnimation(targetUrl) {
  // Add transition class
  document.body.classList.add('page-transition');
  
  // Wait for animation
  setTimeout(() => {
    window.location.href = targetUrl;
  }, 400);
}
```

## Data Models

### User Model (Existing - No Changes Required)

The existing `User` model in `django_persistence/conversation/models.py` already supports all required fields:

```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### UserPreferences Model (Existing - No Changes Required)

The existing `UserPreferences` model already exists and is created automatically on registration.

### Django Admin Configuration

**File**: `django_persistence/conversation/admin.py`

**Configuration**:
```python
from django.contrib import admin
from .models import User, UserPreferences

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'display_name', 'created_at', 'is_active']
    list_filter = ['is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'display_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'display_name', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login')
        }),
    )

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_voice', 'preferred_language']
    search_fields = ['user__email', 'user__display_name']
```

## Routing and Navigation

### Updated Flask Routes

**File**: `flask_frontend/app.py`

**Route Changes**:

1. **Root Route** (`/`):
   - Current: Redirects to `/chat`
   - New: Redirects to `/landing` if not authenticated, else `/chat`

2. **Landing Route** (`/landing`) - NEW:
   - Displays landing dashboard
   - Redirects to `/chat` if already authenticated

3. **Login Route** (`/login`):
   - GET: Display new split-screen login page
   - POST: Process login, redirect to `/chat` on success

4. **Signup Route** (`/signup`):
   - GET: Display new split-screen signup page
   - POST: Process registration, show toast, redirect to `/login` on success

5. **Chat Route** (`/chat`):
   - Current: Allows guest access
   - New: Requires authentication, redirects to `/landing` if not authenticated

### Navigation Flow Diagram

```mermaid
graph TD
    A[User visits /] --> B{Authenticated?}
    B -->|No| C[/landing]
    B -->|Yes| D[/chat]
    
    C --> E{User Action}
    E -->|Click Login| F[/login]
    E -->|Click Signup| G[/signup]
    
    F --> H{Login Success?}
    H -->|Yes| D
    H -->|No| F
    
    G --> I{Signup Success?}
    I -->|Yes| J[Show Toast]
    J --> F
    I -->|No| G
    
    D --> K[Full App Access]
```

## Styling and Design System

### Color Palette (VoyageAI Design System)

**Primary Colors**:
- Primary: `#137fec` (VoyageAI Blue)
- Primary Hover: `#0f6fd4`
- Background Light: `#f6f7f8`
- Background Dark: `#101922`

**Neutral Colors (Tailwind Slate)**:
- Slate 900: `#0f172a` (Dark backgrounds)
- Slate 800: `#1e293b` (Card backgrounds)
- Slate 700: `#334155` (Borders)
- Slate 600: `#475569` (Secondary text)
- Slate 500: `#64748b` (Muted text)
- Slate 400: `#94a3b8` (Placeholder text)
- Slate 300: `#cbd5e1` (Light borders)
- Slate 200: `#e2e8f0` (Light backgrounds)
- White: `#ffffff` (Text on dark)

**Accent Colors**:
- Red 500: `#ef4444` (Weak password indicator)
- Green 500: `#10b981` (Success states)
- Gray 200: `#e5e7eb` (Dividers)
- Gray 300: `#d1d5db` (Light text)

### Typography (VoyageAI Design System)

**Font Stack**:
```css
font-family: 'Plus Jakarta Sans', sans-serif;
```

**Font Import**:
```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap" rel="stylesheet"/>
```

**Type Scale**:
- Display (Hero): 48px / 3rem, font-weight: 800 (font-black)
- Heading 1: 36px / 2.25rem, font-weight: 800 (font-black)
- Heading 2: 32px / 2rem, font-weight: 700 (font-bold)
- Heading 3: 24px / 1.5rem, font-weight: 700 (font-bold)
- Body Large: 18px / 1.125rem, font-weight: 400 (font-normal)
- Body: 16px / 1rem, font-weight: 400 (font-normal)
- Small: 14px / 0.875rem, font-weight: 400 (font-normal)
- Tiny: 12px / 0.75rem, font-weight: 400 (font-normal)

**Font Weights**:
- Normal: 400
- Medium: 500
- Bold: 700
- Black: 800

### Component Styles (Tailwind CSS Approach)

**Button Styles**:
```html
<!-- Primary Button -->
<button class="flex h-12 min-w-[84px] cursor-pointer items-center justify-center overflow-hidden rounded-lg bg-primary px-5 text-base font-bold leading-normal tracking-wide text-white hover:bg-opacity-90 transition-colors">
  <span class="truncate">Log In</span>
</button>


```

**Input Styles**:
```html
<input class="form-input h-12 w-full flex-1 resize-none overflow-hidden rounded-lg border border-slate-300 bg-background-light p-3 text-base font-normal leading-normal text-slate-900 placeholder-slate-400 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 dark:border-slate-700 dark:bg-slate-800 dark:text-white dark:placeholder-slate-500 dark:focus:border-primary" 
       placeholder="Enter your email" 
       type="email" />
```

**Card Styles (Feature Cards)**:
```html
<div class="flex flex-1 gap-3 rounded-lg border border-gray-200 dark:border-[#324d67] bg-white dark:bg-[#192633] p-4 flex-col hover:border-primary transition-colors">
  <div class="text-primary">
    <span class="material-symbols-outlined">flight</span>
  </div>
  <div class="flex flex-col gap-1">
    <h2 class="text-slate-800 dark:text-white text-base font-bold leading-tight">Find Flights</h2>
    <p class="text-gray-500 dark:text-[#92adc9] text-sm font-normal leading-normal">Get the best real-time deals...</p>
  </div>
</div>
```

**Material Symbols Icons**:
```html
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>

<style>
  .material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  }
</style>

<span class="material-symbols-outlined">travel_explore</span>
```

### Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {
  .split-screen {
    flex-direction: column;
  }
  .split-left, .split-right {
    width: 100%;
  }
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  .split-left {
    width: 45%;
  }
  .split-right {
    width: 55%;
  }
}

/* Desktop */
@media (min-width: 1025px) {
  /* Default split-screen layout */
}
```

## Error Handling

### Client-Side Validation

**Email Validation**:
- Check for valid email format
- Display inline error if invalid
- Prevent form submission

**Password Validation**:
- Minimum 8 characters
- Display strength indicator
- Match confirmation password
- Show inline errors

**Display Name Validation**:
- Required field
- Minimum 2 characters
- Maximum 100 characters

### Server-Side Error Handling

**Django API Errors**:
- 400 Bad Request: Display validation errors inline
- 401 Unauthorized: Display "Invalid credentials" message
- 500 Server Error: Display generic error message
- Network Error: Display "Unable to connect" message

**Error Display Strategy**:
- Inline errors below form fields
- Toast notifications for critical errors
- Maintain form data on error (don't clear inputs)
- Focus first error field

### Toast Notification Errors

**Registration Errors**:
- Email already exists
- Password too weak
- Network connection failed

**Login Errors**:
- Invalid credentials
- Account disabled
- Network connection failed

## Testing Strategy

### Manual Testing Checklist

**Landing Dashboard**:
- [ ] Landing page displays correctly
- [ ] Branding elements visible
- [ ] Login button navigates to login page
- [ ] Signup button navigates to signup page
- [ ] Authenticated users redirect to chat
- [ ] Responsive on mobile devices

**Login Page**:
- [ ] Split-screen layout displays correctly
- [ ] Form validation works
- [ ] Successful login redirects to chat
- [ ] Failed login shows error message
- [ ] Signup link navigates with animation
- [ ] Responsive on mobile (stacked layout)

**Signup Page**:
- [ ] Split-screen layout displays correctly
- [ ] Form validation works
- [ ] Password confirmation validates
- [ ] Successful signup shows toast
- [ ] Successful signup redirects to login
- [ ] Failed signup shows errors
- [ ] Login link navigates with animation
- [ ] Responsive on mobile (stacked layout)

**Page Transitions**:
- [ ] Login to signup animates smoothly
- [ ] Signup to login animates smoothly
- [ ] Animation duration under 500ms
- [ ] No visual glitches during transition

**Toast Notifications**:
- [ ] Success toast displays on registration
- [ ] Toast auto-dismisses after 3 seconds
- [ ] Toast is dismissible by clicking X
- [ ] Multiple toasts stack correctly

**Django Admin**:
- [ ] User model registered in admin
- [ ] User list displays email, name, date
- [ ] User detail view shows all fields
- [ ] Search functionality works
- [ ] Filters work correctly
- [ ] UserPreferences visible in admin

**Authentication Flow**:
- [ ] Guest mode completely removed
- [ ] Unauthenticated users cannot access chat
- [ ] Session persists across page reloads
- [ ] Logout clears session properly
- [ ] User profile stored in database
- [ ] All user fields populated correctly

### Browser Compatibility

**Target Browsers**:
- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

**CSS Features to Test**:
- CSS Grid and Flexbox layouts
- CSS animations and transitions
- CSS custom properties (variables)
- Backdrop filters (if used)

### Performance Considerations

**Page Load Performance**:
- Minimize CSS file size
- Optimize images (use WebP where possible)
- Lazy load non-critical assets
- Target < 2s initial page load

**Animation Performance**:
- Use CSS transforms (GPU-accelerated)
- Avoid animating layout properties
- Use `will-change` for animated elements
- Target 60fps for all animations

## Security Considerations

### CSRF Protection

- Django CSRF tokens required for all POST requests
- Flask must pass CSRF tokens to forms
- Validate tokens on Django backend

### Password Security

- Passwords hashed using Django's default (PBKDF2)
- Minimum 8 character requirement
- No password strength requirements (Django default)
- Passwords never logged or displayed

### Session Security

- HTTP-only session cookies
- Secure flag in production (HTTPS)
- Session timeout after inactivity
- Logout clears session completely

### Input Sanitization

- Django ORM prevents SQL injection
- HTML escaping in templates (Jinja2 auto-escape)
- Email validation on client and server
- Display name sanitized for XSS

## Implementation Notes

### File Structure

```
flask_frontend/
├── templates/
│   ├── landing.html (REDESIGN - VoyageAI welcome screen)
│   ├── login.html (REDESIGN - VoyageAI login with split-screen)
│   ├── signup.html (REDESIGN - VoyageAI signup with split-screen)
│   ├── base.html (UPDATE - Add Tailwind CDN, Material Symbols, Plus Jakarta Sans)
│   └── ...
├── static/
│   ├── css/
│   │   ├── style.css (UPDATE - Minimal custom CSS, mostly Tailwind)
│   │   ├── landing.css (OPTIONAL - Custom landing styles if needed)
│   │   └── auth.css (OPTIONAL - Custom auth styles if needed)
│   ├── js/
│   │   ├── toast.js (EXISTING - Keep for notifications)
│   │   ├── transitions.js (EXISTING - Keep for page transitions)
│   │   └── validation.js (EXISTING - Keep for form validation)
│   └── images/
│       ├── world-map-bg.jpg (NEW - For login branding panel)
│       └── globe-bg.jpg (NEW - For signup branding panel)
└── app.py (UPDATE - Routing logic)

django_persistence/
└── conversation/
    ├── admin.py (EXISTING - Already configured)
    └── ...
```

**Key Changes**:
- Use Tailwind CSS CDN instead of custom CSS files
- Import Material Symbols icon font
- Import Plus Jakarta Sans from Google Fonts
- Add background images for branding panels
- Minimal custom CSS needed (Tailwind handles most styling)

### Dependencies

**No new Python dependencies required**

**Frontend Assets**:
- Tailwind CSS (via CDN): `https://cdn.tailwindcss.com?plugins=forms,container-queries`
- Plus Jakarta Sans font (via Google Fonts): `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap`
- Material Symbols icons (via Google Fonts): `https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200`
- Existing toast.js for notifications
- Existing transitions.js for page animations
- Existing validation.js for form validation
- No JavaScript framework required (vanilla JS sufficient)

**Tailwind Configuration**:
```javascript
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "#137fec",
        "background-light": "#f6f7f8",
        "background-dark": "#101922",
      },
      fontFamily: {
        "display": ["Plus Jakarta Sans", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "full": "9999px"
      },
    },
  },
}
```

### Deployment Considerations

**Environment Variables**:
- No new environment variables required
- Existing Django and Flask configs sufficient

**Database Migrations**:
- No database schema changes required
- Existing User and UserPreferences models sufficient

**Static Files**:
- Collect static files for production
- Optimize and minify CSS/JS
- Compress images

### Accessibility

**WCAG 2.1 AA Compliance**:
- Proper heading hierarchy
- Sufficient color contrast (4.5:1 minimum)
- Keyboard navigation support
- Focus indicators visible
- Form labels associated with inputs
- Error messages announced to screen readers
- Alt text for all images

**ARIA Attributes**:
```html
<button aria-label="Login to your account">Login</button>
<div role="alert" aria-live="polite"><!-- Toast notification --></div>
<form aria-labelledby="login-heading">...</form>
```

## Future Enhancements

### Phase 2 Considerations

1. **Social Authentication**:
   - Google OAuth integration
   - GitHub OAuth integration
   - Microsoft OAuth integration

2. **Password Recovery**:
   - Forgot password flow
   - Email verification
   - Password reset tokens

3. **Email Verification**:
   - Verify email on registration
   - Resend verification email
   - Email change verification

4. **Two-Factor Authentication**:
   - TOTP-based 2FA
   - SMS-based 2FA
   - Backup codes

5. **Enhanced Animations**:
   - Micro-interactions on form inputs
   - Loading skeletons
   - Page transition effects
   - Parallax scrolling on landing

6. **Onboarding Flow**:
   - Welcome tour for new users
   - Feature highlights
   - Preference setup wizard

7. **Dark/Light Mode Toggle**:
   - User preference for theme
   - System preference detection
   - Smooth theme transitions
