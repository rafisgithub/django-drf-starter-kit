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
    
    # Get domain setting from Django settings
    domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
    
    
    # Determine SameSite value
    # For cross-origin requests with credentials, use 'None' with Secure=True
    # For same-origin, 'Lax' is sufficient
    samesite = settings.CSRF_COOKIE_SAMESITE

    
    # Access token cookie
    response.set_cookie(
        key='access_token',
        value=access_token,
        domain=domain,  # None = current domain, '.domain.com' = all subdomains
        httponly=True,  # XSS protection
        secure=secure,  # HTTPS only in production
        samesite=samesite,  # CSRF protection
        max_age=getattr(settings, 'ACCESS_TOKEN_COOKIE_MAX_AGE', 3600)  # 1 hour default
    )
    
    # Refresh token cookie
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        domain=domain,  # None = current domain, '.domain.com' = all subdomains
        httponly=True,  # XSS protection
        secure=secure,  # HTTPS only in production
        samesite=samesite,  # CSRF protection
        max_age=getattr(settings, 'REFRESH_TOKEN_COOKIE_MAX_AGE', 86400 * 7)  # 7 days default
    )
    
    return response


def clear_auth_cookies(response):

    domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
    samesite = settings.CSRF_COOKIE_SAMESITE
    secure = settings.SESSION_COOKIE_SECURE
    
    # Manually expire cookies to support 'secure' attribute which delete_cookie may not accept
    response.set_cookie(
        'access_token', 
        value='', 
        max_age=0, 
        expires='Thu, 01 Jan 1970 00:00:00 GMT', 
        domain=domain, 
        samesite=samesite, 
        secure=secure,
        httponly=True 
    )
    response.set_cookie(
        'refresh_token', 
        value='', 
        max_age=0, 
        expires='Thu, 01 Jan 1970 00:00:00 GMT', 
        domain=domain, 
        samesite=samesite, 
        secure=secure, 
        httponly=True
    )
    return response


def create_hybrid_auth_response(data, tokens, request, message="Authentication successful", status_code=200):
   
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
        response_data = {'user': data}
        response = success(
            data=response_data,
            message=message,
            status_code=status_code
        )
        
        # Use the SESSION_COOKIE_SECURE setting which is configured based on CROSS_ORIGIN_DEVELOPMENT
        secure = settings.SESSION_COOKIE_SECURE
        set_auth_cookies(response, tokens['access'], tokens['refresh'], secure=secure)
    
    return response


def create_hybrid_refresh_response(tokens, request, message="Token refreshed successfully", status_code=200):
  
    
    # Determine client type
    is_mobile = getattr(request, 'is_mobile_client', False)
    
    if is_mobile:
        # Mobile: Return tokens in response body
        response_data = {
            'tokens': {
                'access': tokens['access'],
                'refresh': tokens.get('refresh')  
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
        secure = not settings.DEBUG
        domain = getattr(settings, 'SESSION_COOKIE_DOMAIN', None)
        samesite = settings.CSRF_COOKIE_SAMESITE
                
        response.set_cookie(
            key='access_token',
            value=tokens['access'],
            domain=domain,
            httponly=True,
            secure=secure,
            samesite=samesite,
            max_age=getattr(settings, 'ACCESS_TOKEN_COOKIE_MAX_AGE', 3600)
        )
        
        # Set refresh token if present (token rotation)
        if 'refresh' in tokens and tokens['refresh']:
            response.set_cookie(
                key='refresh_token',
                value=tokens['refresh'],
                domain=domain,
                httponly=True,
                secure=secure,
                samesite=samesite,
                max_age=getattr(settings, 'REFRESH_TOKEN_COOKIE_MAX_AGE', 86400 * 7)
            )
            
    
    return response
