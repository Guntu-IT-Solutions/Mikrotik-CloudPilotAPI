from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import APIKey
from django.contrib.auth.models import User


class PublicKeyAuthentication(BaseAuthentication):
    """
    Authentication class that validates requests using the user's public API key.
    Used for IntaSend payment operations where clients provide their public key.
    """
    
    def authenticate(self, request):
        # Get the public key from the request header
        public_key = request.META.get('HTTP_X_PUBLIC_KEY') or request.META.get('HTTP_PUBLIC_KEY')
        
        if not public_key:
            raise AuthenticationFailed(
                'Public API key is required. Please include your public API key in the X-Public-Key header. '
                'Example: X-Public-Key: your_public_key_here'
            )
        
        # Validate public key format (should be 32 characters hex)
        if len(public_key) != 32 or not all(c in '0123456789abcdef' for c in public_key.lower()):
            raise AuthenticationFailed(
                'Invalid public API key format. The public key should be a 32-character hexadecimal string. '
                'Please check your API key and try again.'
            )
        
        try:
            # Find the user by public key
            api_key = APIKey.objects.get(public_key=public_key)
            user = api_key.user
            
            if not user.is_active:
                raise AuthenticationFailed(
                    'User account is disabled. Please contact support to reactivate your account.'
                )
            
            return (user, None)
            
        except APIKey.DoesNotExist:
            raise AuthenticationFailed(
                'Invalid public API key. The provided key does not exist in our system. '
                'Please check your API key and ensure it matches the one generated for your account.'
            )
        except Exception as e:
            raise AuthenticationFailed(
                f'Authentication failed due to a system error: {str(e)}. '
                'Please try again or contact support if the issue persists.'
            )
    
    def authenticate_header(self, request):
        return 'PublicKey realm="IntaSend Payments"'
