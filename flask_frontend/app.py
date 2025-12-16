import os
from flask import Flask, render_template, redirect, url_for, request, session as flask_session
from dotenv import load_dotenv
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Load local .env (same folder) so you don't need to export env vars manually
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)

# Configuration: where the FastAPI backend is, and the LiveKit URL to connect the browser client
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
# Use ws:// (or wss://) for LiveKit URL; http:// would be incorrect for WebSocket
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://127.0.0.1:7880")  # e.g., wss://your-livekit-host
DEFAULT_ROOM = os.getenv("DEFAULT_ROOM", "quickstart")
# Optional: pass through a system prompt for agent initialization
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a friendly travel assistant.")
# Django API URL for authentication (without /api suffix - it's added in the routes)
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://127.0.0.1:8000").rstrip("/")

# Debug: Print configuration on startup
print("=" * 60)
print("Flask Configuration:")
print(f"  FASTAPI_BASE_URL: {FASTAPI_BASE_URL}")
print(f"  LIVEKIT_URL: {LIVEKIT_URL}")
print(f"  DJANGO_API_URL: {DJANGO_API_URL}")
print("=" * 60)


@app.route("/health")
def health():
    """Health check endpoint for Azure App Service"""
    return {"status": "healthy", "service": "flask-frontend"}, 200


@app.route("/")
def index():
    # Check authentication status
    user = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
    except requests.exceptions.RequestException:
        # If Django is unreachable, treat as unauthenticated
        pass
    
    # Redirect based on authentication status
    if user:
        return redirect(url_for("chat"))
    else:
        return redirect(url_for("landing"))


@app.route("/landing")
def landing():
    # Check authentication status
    user = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
    except requests.exceptions.RequestException:
        # If Django is unreachable, treat as unauthenticated
        pass
    
    # Redirect authenticated users to chat
    if user:
        return redirect(url_for("chat"))
    
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        
        try:
            # Forward credentials to Django API
            response = requests.post(
                f"{DJANGO_API_URL}/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Django sets session cookie via Set-Cookie header
                # We need to pass it through to the browser
                resp = redirect(url_for("chat"))
                
                # Extract sessionid cookie from Django response
                if 'sessionid' in response.cookies:
                    session_cookie = response.cookies['sessionid']
                    
                    # Store in Flask session as backup
                    flask_session['django_sessionid'] = session_cookie
                    
                    # Set the cookie with proper attributes
                    resp.set_cookie(
                        'sessionid',
                        session_cookie,
                        max_age=1209600,  # 14 days
                        httponly=True,
                        samesite='Lax',
                        secure=False,  # Set to True in production with HTTPS
                        path='/'
                    )
                    print(f"✓ Login successful - Set sessionid cookie: {session_cookie[:10]}...")
                else:
                    print("✗ Warning: No sessionid cookie in Django response")
                
                return resp
            else:
                # Parse error response from Django
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                errors = {}
                
                # Check if it's a field-specific error or general error
                if isinstance(error_data, dict):
                    # Handle field-specific errors
                    for field in ['email', 'password']:
                        if field in error_data:
                            # Extract error message (could be string or list)
                            field_error = error_data[field]
                            if isinstance(field_error, list):
                                errors[field] = field_error[0] if field_error else 'Invalid value'
                            else:
                                errors[field] = str(field_error)
                    
                    # Handle general error message
                    if 'detail' in error_data and not errors:
                        errors['general'] = error_data['detail']
                    elif not errors:
                        errors['general'] = 'Invalid credentials'
                else:
                    errors['general'] = 'Invalid credentials'
                
                return render_template("login.html", errors=errors, email=email)
        except requests.exceptions.RequestException as e:
            errors = {'general': f"Unable to connect to authentication service: {str(e)}"}
            return render_template("login.html", errors=errors, email=email)
    
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        errors = {}
        
        # Simple validation
        if not email:
            errors['email'] = "Email is required"
        if not username:
            errors['username'] = "Username is required"
        if not password:
            errors['password'] = "Password is required"
        if not confirm_password:
            errors['confirm_password'] = "Please confirm your password"
        elif password != confirm_password:
            errors['confirm_password'] = "Passwords do not match"
        
        if errors:
            return render_template("signup.html", errors=errors, email=email, username=username)
        
        try:
            # Forward registration data to Django API
            response = requests.post(
                f"{DJANGO_API_URL}/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "display_name": username  # Use username as display_name
                },
                timeout=10
            )
            
            if response.status_code == 201:
                # Registration successful - redirect to login
                return render_template("signup.html", success=True)
            else:
                # Parse validation errors from Django
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                
                if isinstance(error_data, dict):
                    # Handle field-specific errors
                    for field in ['email', 'password', 'display_name']:
                        if field in error_data:
                            field_error = error_data[field]
                            if isinstance(field_error, list):
                                errors[field if field != 'display_name' else 'username'] = field_error[0] if field_error else 'Invalid value'
                            else:
                                errors[field if field != 'display_name' else 'username'] = str(field_error)
                    
                    # Handle general error message
                    if 'detail' in error_data and not errors:
                        errors['general'] = error_data['detail']
                    elif not errors:
                        errors['general'] = 'Registration failed. Please try again.'
                else:
                    errors['general'] = 'Registration failed. Please try again.'
                
                return render_template("signup.html", errors=errors, email=email, username=username)
        except requests.exceptions.RequestException as e:
            errors = {'general': f"Unable to connect to server. Please try again."}
            return render_template("signup.html", errors=errors, email=email, username=username)
    
    return render_template("signup.html")


@app.route("/logout")
def logout():
    try:
        # Call Django logout endpoint
        # Pass along any cookies from the browser request
        cookies = request.cookies
        requests.post(
            f"{DJANGO_API_URL}/auth/logout",
            cookies=cookies,
            timeout=10
        )
    except requests.exceptions.RequestException:
        # Even if Django logout fails, we still redirect to home
        pass
    
    # Redirect to home page
    resp = redirect(url_for("index"))
    # Clear the session cookie on the client side
    resp.set_cookie('sessionid', '', expires=0)
    return resp


@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Check authentication
    user = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
        else:
            # Not authenticated, redirect to login
            return redirect(url_for("login"))
    except requests.exceptions.RequestException:
        # If Django is unreachable, redirect to login
        return redirect(url_for("login"))
    
    # Fetch user profile from Django /api/users/profile
    profile_data = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/users/profile",
            cookies=cookies,
            timeout=10
        )
        if response.status_code == 200:
            profile_data = response.json()
    except requests.exceptions.RequestException:
        # If Django is unreachable, show error
        return render_template("error.html",
                             user=user,
                             error_title="Service Unavailable",
                             error_message="Unable to connect to the profile service."), 503
    
    # Handle form submissions
    success_message = None
    error_message = None
    
    if request.method == "POST":
        form_type = request.form.get("form_type")
        
        if form_type == "update_profile":
            # Update display_name
            try:
                cookies = request.cookies
                response = requests.patch(
                    f"{DJANGO_API_URL}/users/profile",
                    json={
                        "display_name": request.form.get("display_name")
                    },
                    cookies=cookies,
                    timeout=10
                )
                if response.status_code == 200:
                    profile_data = response.json()
                    success_message = "Profile updated successfully!"
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                    error_message = error_data.get('detail', 'Failed to update profile')
            except requests.exceptions.RequestException as e:
                error_message = f"Unable to connect to the profile service: {str(e)}"
        
        elif form_type == "update_preferences":
            # Update preferences
            try:
                # Parse favorite_topics from comma-separated string
                topics_str = request.form.get("favorite_topics", "")
                favorite_topics = [t.strip() for t in topics_str.split(",") if t.strip()]
                
                cookies = request.cookies
                response = requests.put(
                    f"{DJANGO_API_URL}/users/preferences",
                    json={
                        "preferred_voice": request.form.get("preferred_voice"),
                        "preferred_language": request.form.get("preferred_language"),
                        "favorite_topics": favorite_topics,
                        "system_prompt_override": request.form.get("system_prompt_override", "")
                    },
                    cookies=cookies,
                    timeout=10
                )
                if response.status_code == 200:
                    # Refresh profile data to show updated preferences
                    cookies = request.cookies
                    profile_response = requests.get(
                        f"{DJANGO_API_URL}/users/profile",
                        cookies=cookies,
                        timeout=10
                    )
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                    success_message = "Preferences updated successfully!"
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                    error_message = error_data.get('detail', 'Failed to update preferences')
            except requests.exceptions.RequestException as e:
                error_message = f"Unable to connect to the profile service: {str(e)}"
        
        elif form_type == "change_password":
            # Change password
            try:
                cookies = request.cookies
                response = requests.post(
                    f"{DJANGO_API_URL}/users/change-password",
                    json={
                        "current_password": request.form.get("current_password"),
                        "new_password": request.form.get("new_password")
                    },
                    cookies=cookies,
                    timeout=10
                )
                if response.status_code == 200:
                    success_message = "Password changed successfully!"
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                    # Handle validation errors
                    if isinstance(error_data, dict):
                        if 'current_password' in error_data:
                            error_message = error_data['current_password'][0] if isinstance(error_data['current_password'], list) else error_data['current_password']
                        elif 'new_password' in error_data:
                            error_message = error_data['new_password'][0] if isinstance(error_data['new_password'], list) else error_data['new_password']
                        else:
                            error_message = error_data.get('detail', 'Failed to change password')
                    else:
                        error_message = 'Failed to change password'
            except requests.exceptions.RequestException as e:
                error_message = f"Unable to connect to the profile service: {str(e)}"
    
    return render_template("profile.html", 
                         user=user, 
                         profile=profile_data,
                         success_message=success_message,
                         error_message=error_message)


@app.route("/history")
def history():
    # Check authentication by calling Django /api/auth/me
    user = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
        else:
            # Not authenticated, redirect to login
            return redirect(url_for("login"))
    except requests.exceptions.RequestException:
        # If Django is unreachable, redirect to login
        return redirect(url_for("login"))
    
    # Fetch user's sessions from Django /api/users/history
    sessions = []
    total_count = 0
    has_more = False
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/users/history",
            cookies=cookies,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('results', [])
            total_count = data.get('count', 0)
            has_more = data.get('next') is not None
    except requests.exceptions.RequestException:
        # If Django is unreachable, show empty history
        pass
    
    return render_template("history.html", user=user, sessions=sessions, total_count=total_count, has_more=has_more)


@app.route("/history/<session_id>")
def history_detail(session_id):
    # Check authentication
    user = None
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
        else:
            # Not authenticated, redirect to login
            return redirect(url_for("login"))
    except requests.exceptions.RequestException:
        # If Django is unreachable, redirect to login
        return redirect(url_for("login"))
    
    # Fetch session details from Django /api/users/history/{session_id}
    try:
        cookies = request.cookies
        response = requests.get(
            f"{DJANGO_API_URL}/users/history/{session_id}",
            cookies=cookies,
            timeout=10
        )
        if response.status_code == 200:
            session_data = response.json()
            return render_template("history_detail.html", user=user, session=session_data)
        elif response.status_code == 404:
            # Session not found or doesn't belong to user
            return render_template("error.html", 
                                 user=user,
                                 error_title="Session Not Found",
                                 error_message="This conversation could not be found or does not belong to you."), 404
        else:
            # Other error
            return render_template("error.html",
                                 user=user,
                                 error_title="Error",
                                 error_message="Unable to load conversation details."), 500
    except requests.exceptions.RequestException as e:
        # If Django is unreachable
        return render_template("error.html",
                             user=user,
                             error_title="Service Unavailable",
                             error_message=f"Unable to connect to the history service: {str(e)}"), 503


@app.route("/chat")
def chat():
    # Check authentication status - REQUIRED for chat access
    user = None
    try:
        # Try to get cookies from request
        cookies = dict(request.cookies)
        
        # Fallback: if sessionid not in cookies, try Flask session
        if 'sessionid' not in cookies and 'django_sessionid' in flask_session:
            cookies['sessionid'] = flask_session['django_sessionid']
            print(f"Using sessionid from Flask session: {cookies['sessionid'][:10]}...")
        
        response = requests.get(
            f"{DJANGO_API_URL}/auth/me",
            cookies=cookies,
            timeout=5
        )
        if response.status_code == 200:
            user = response.json()
            print(f"✓ Auth check successful for user: {user.get('email', 'unknown')}")
        else:
            # Not authenticated, redirect to landing
            print(f"✗ Auth check failed with status {response.status_code}")
            print(f"  Cookies sent: {list(cookies.keys())}")
            return redirect(url_for("landing"))
    except requests.exceptions.RequestException as e:
        # If Django is unreachable, redirect to landing (no guest mode)
        print(f"✗ Auth check failed with exception: {e}")
        return redirect(url_for("landing"))
    
    # If we got here but user is None, redirect to landing
    if not user:
        print("✗ User is None after auth check")
        return redirect(url_for("landing"))
    
    # Pass runtime config into the page so static JS can consume it.
    config = {
        "fastapiBaseUrl": FASTAPI_BASE_URL,
        "livekitUrl": LIVEKIT_URL,
        "defaultRoom": DEFAULT_ROOM,
        "systemPrompt": SYSTEM_PROMPT,
        "djangoApiUrl": DJANGO_API_URL,  # Add Django API URL for session save
        "user": user  # Pass user data to template and JavaScript
    }
    return render_template("chat.html", config=config)


if __name__ == "__main__":
    # Run on port 5173 by default to match existing CORS allowlist in FastAPI
    port = int(os.getenv("PORT", "5173"))
    app.run(host="127.0.0.1", port=port, debug=True)
