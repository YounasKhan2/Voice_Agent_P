"""
Authentication utilities for validating user sessions with Django backend.
"""
import httpx
from typing import Optional, Dict
import logging

from ..config import get_settings

logger = logging.getLogger("voice-agent")


async def validate_session_cookie(session_cookie: str) -> Optional[Dict]:
    """
    Validate session cookie with Django backend.
    
    Args:
        session_cookie: The session cookie value to validate
        
    Returns:
        User data dict if valid (containing user_id, email, display_name, preferences),
        None if invalid or on error
        
    Example return value:
        {
            "valid": True,
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "display_name": "John Doe",
            "preferences": {
                "preferred_voice": "nova",
                "preferred_language": "en",
                "favorite_topics": ["travel", "technology"],
                "system_prompt_override": ""
            }
        }
    """
    settings = get_settings()
    
    # If Django base URL not configured, return None (anonymous mode)
    if not settings.django_base_url:
        logger.debug("Django base URL not configured, skipping session validation")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.django_base_url}/api/internal/validate-session",
                cookies={"sessionid": session_cookie},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('valid'):
                    logger.info(f"Session validated for user: {data.get('email')}")
                    return data
                else:
                    logger.debug("Session validation returned invalid")
                    return None
            else:
                logger.debug(f"Session validation failed with status: {response.status_code}")
                return None
                
    except httpx.TimeoutException:
        logger.warning("Session validation timed out, falling back to anonymous mode")
        return None
    except httpx.RequestError as e:
        logger.warning(f"Session validation request error: {e}, falling back to anonymous mode")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during session validation: {e}, falling back to anonymous mode")
        return None
