from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from django.conf import settings

def enforce_csrf(request):
    """
    Enforce CSRF protection for cookie-based authentication.
    Only enabled for web clients using cookie authentication.
    """
    check = CSRFCheck(request)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied(f'CSRF Failed: {reason}')


class HybridJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        # Detect client type (set by ClientTypeMiddleware)
        is_mobile = getattr(request, 'is_mobile_client', False)
        
        # Step 1: Try Authorization header first (mobile/API clients)
        header = self.get_header(request)
        if header is not None:
            raw_token = self.get_raw_token(header)
        else:
            raw_token = None
        
        # Step 2: Fallback to cookies (web clients)
        if raw_token is None:
            raw_token = request.COOKIES.get('access_token') or None
        
        # Handle common frontend error: token value is literally "null"
        if raw_token is not None:
            temp_token = raw_token.decode('utf-8') if isinstance(raw_token, bytes) else raw_token
            if temp_token == 'null':
                raw_token = request.COOKIES.get('access_token') or None

        if raw_token is None:
            return None
        
        # Ensure token is string and clean
        if isinstance(raw_token, bytes):
            raw_token = raw_token.decode('utf-8')
        
        # Strip potential quotes from cookie value
        raw_token = raw_token.strip('"')

        # Validate the token
        validated_token = self.get_validated_token(raw_token)
        
        # SECURITY: User-Agent binding validation
        # Configurable - set ENABLE_USER_AGENT_BINDING in settings
        if getattr(settings, 'ENABLE_USER_AGENT_BINDING', True):
            self._validate_user_agent(request, validated_token)
        
        # SECURITY: CSRF protection for cookie-based auth
        # Only enforce for web clients using cookies
        if not is_mobile and 'access_token' in request.COOKIES:
            if getattr(settings, 'ENABLE_CSRF_FOR_COOKIES', False):
                enforce_csrf(request)
        
        return self.get_user(validated_token), validated_token
    
    def _validate_user_agent(self, request, validated_token):
        """
        Validate User-Agent binding to prevent token theft.
        Tokens are bound to the User-Agent that created them.
        """
        from .utils import get_user_agent_hash
        
        token_ua_hash = validated_token.get('user_agent')
        current_ua_hash = get_user_agent_hash(request)
        
        if token_ua_hash and token_ua_hash != current_ua_hash:
            # Log for security monitoring
            print(f"SECURITY WARNING: User-Agent Mismatch! Token UA: {token_ua_hash}, Request UA: {current_ua_hash}")
            raise exceptions.AuthenticationFailed('Token is invalid (User-Agent Mismatch).')


# Legacy alias for backward compatibility
CookieJWTAuthentication = HybridJWTAuthentication
