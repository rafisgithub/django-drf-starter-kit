import secrets
from django.core.mail import EmailMessage
from django.conf import settings
import hashlib
from apps.utils.helpers import success


def generate_otp(length=6):
    digits = '0123456789'
    return ''.join(secrets.choice(digits) for _ in range(length))

def send_normal_mail(data):
    email = EmailMessage(
        subject=data['subject'],
        body=data['body'],
        from_email=settings.EMAIL_HOST_USER,
        to=data['to']
    )
    email.send()

def get_client_ip(request):
    """
    Get the client authentication IP address from specific request object.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent_hash(request):
    """
    Get the SHA-256 hash of the User-Agent string.
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not user_agent:
        return None
    
    # Hash the user agent
    hash_object = hashlib.sha256(user_agent.encode('utf-8'))
    return hash_object.hexdigest()


# ============================================
# Hybrid Authentication Response Utilities
# ============================================

def set_auth_cookies(response, access_token, refresh_token, secure=False):
    """
    Set HttpOnly authentication cookies for web clients.
    
    Args:
        response: Django Response object
        access_token: JWT access token
        refresh_token: JWT refresh token
        secure: Whether to use Secure flag (HTTPS only) - should be True in production
    
    Security Features:
    - HttpOnly: Prevents JavaScript access (XSS protection)
    - Secure: HTTPS only (should be True in production)
    - SameSite: CSRF protection
    """
    # Access token cookie
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,  # XSS protection
        secure=secure,  # HTTPS only in production
        samesite='Lax',  # CSRF protection (use 'Strict' for more security)
        max_age=getattr(settings, 'ACCESS_TOKEN_COOKIE_MAX_AGE', 3600)  # 1 hour default
    )
    
    # Refresh token cookie
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,  # XSS protection
        secure=secure,  # HTTPS only in production
        samesite='Lax',  # CSRF protection
        max_age=getattr(settings, 'REFRESH_TOKEN_COOKIE_MAX_AGE', 86400 * 7)  # 7 days default
    )
    
    return response


def clear_auth_cookies(response):
    """
    Clear authentication cookies on logout.
    
    Args:
        response: Django Response object
    """
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response


def create_hybrid_auth_response(data, tokens, request, message="Authentication successful", status_code=200):
    """
    Create hybrid authentication response based on client type.
    
    For Web clients:
        - Returns user data only in response body
        - Sets tokens in HttpOnly cookies
    
    For Mobile clients:
        - Returns user data AND tokens in response body
        - No cookies set
    
    Args:
        data: User data to return
        tokens: Dict with 'access' and 'refresh' keys
        request: Django Request object
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Response object with appropriate format for client type
    """
    
    # Determine client type
    is_mobile = getattr(request, 'is_mobile_client', False)
    
    if is_mobile:
        # Mobile: Return tokens in response body
        response_data = {
            'user': data,
            'tokens': {
                'access': tokens['access'],
                'refresh': tokens['refresh']
            }
        }
        response = success(
            data=response_data,
            message=message,
            status_code=status_code
        )
    else:
        # Web: Return only user data, tokens in cookies
        response_data = {'user': data}
        response = success(
            data=response_data,
            message=message,
            status_code=status_code
        )
        
        # Set cookies for web clients
        secure = not settings.DEBUG  # Use secure cookies in production
        set_auth_cookies(response, tokens['access'], tokens['refresh'], secure=secure)
    
    return response


def create_hybrid_refresh_response(tokens, request, message="Token refreshed successfully", status_code=200):
    """
    Create hybrid token refresh response based on client type.
    
    For Web clients:
        - Returns empty data or success message
        - Sets new tokens in HttpOnly cookies
    
    For Mobile clients:
        - Returns new tokens in response body
        - No cookies set
    
    Args:
        tokens: Dict with 'access' and optionally 'refresh' keys
        request: Django Request object
        message: Success message
        status_code: HTTP status code
    
    Returns:
        Response object with appropriate format for client type
    """
    
    # Determine client type
    is_mobile = getattr(request, 'is_mobile_client', False)
    
    if is_mobile:
        # Mobile: Return tokens in response body
        response_data = {
            'tokens': {
                'access': tokens['access'],
                'refresh': tokens.get('refresh')  # May not be present if not rotated
            }
        }
        response = success(
            data=response_data,
            message=message,
            status_code=status_code
        )
    else:
        # Web: Return empty data, tokens in cookies
        response = success(
            data={},
            message=message,
            status_code=status_code
        )
        
        # Set cookies for web clients
        secure = not settings.DEBUG  # Use secure cookies in production
        response.set_cookie(
            key='access_token',
            value=tokens['access'],
            httponly=True,
            secure=secure,
            samesite='Lax',
            max_age=getattr(settings, 'ACCESS_TOKEN_COOKIE_MAX_AGE', 3600)
        )
        
        # Set refresh token if present (token rotation)
        if 'refresh' in tokens and tokens['refresh']:
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                httponly=True,
                secure=secure,
                samesite='Lax',
                max_age=getattr(settings, 'REFRESH_TOKEN_COOKIE_MAX_AGE', 86400 * 7)
            )
    
    return response
