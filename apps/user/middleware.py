"""
Hybrid Authentication Middleware
Detects client type (Web/Mobile) and adds context to the request
"""


class ClientTypeMiddleware:
    """
    Middleware to detect client type based on custom header.
    
    Web clients: Send 'X-Client-Type: web' header
    Mobile clients: Send 'X-Client-Type: mobile' header
    
    If no header is provided, defaults to 'web' for backward compatibility.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Detect client type from custom header
        client_type = request.headers.get('X-Client-Type', 'web').lower()
        
        # Validate client type
        if client_type not in ['web', 'mobile']:
            client_type = 'web'  # Default to web for safety
        
        # Add to request for easy access in views
        request.client_type = client_type
        request.is_web_client = client_type == 'web'
        request.is_mobile_client = client_type == 'mobile'
        
        response = self.get_response(request)
        return response
