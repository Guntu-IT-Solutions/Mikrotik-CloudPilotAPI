from django.contrib.auth.models import User
from users.models import APIKey
import hashlib

def validate_api_keys(public_key, private_key):
    """
    Simple function to validate API keys and return user
    Used for API key login to get JWT tokens
    """
    try:
        # Find the API key in the database using public key
        api_key_obj = APIKey.objects.get(public_key=public_key)
        
        # Verify the private key by hashing it and comparing with stored hash
        private_key_hash = hashlib.sha256(private_key.encode()).hexdigest()
        
        if api_key_obj.private_key_hash == private_key_hash:
            return api_key_obj.user
        else:
            return None
            
    except APIKey.DoesNotExist:
        return None
