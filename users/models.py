from django.db import models
from django.contrib.auth.models import User
import secrets, hashlib

class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='api_key')
    public_key = models.CharField(max_length=64, unique=True)
    private_key_hash = models.CharField(max_length=128)  # Store hashed value
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_key(length=32):
        return secrets.token_hex(length // 2)

    @classmethod
    def create_for_user(cls, user):
        public = cls.generate_key(32)
        private = cls.generate_key(64)
        private_hash = hashlib.sha256(private.encode()).hexdigest()
        instance, _ = cls.objects.update_or_create(
            user=user,
            defaults={'public_key': public, 'private_key_hash': private_hash}
        )
        return public, private  # return plain private so user can see it once
    
    @classmethod
    def create_custom_for_user(cls, user, public_key, private_key):
        """Create API keys with custom values provided by user"""
        # Validate key lengths
        if len(public_key) != 32:  # 16 bytes = 32 hex chars
            raise ValueError("Public key must be exactly 32 characters (16 bytes)")
        if len(private_key) != 64:  # 32 bytes = 64 hex chars
            raise ValueError("Private key must be exactly 64 characters (32 bytes)")
        
        # Validate hex format
        try:
            int(public_key, 16)
            int(private_key, 16)
        except ValueError:
            raise ValueError("Keys must be valid hexadecimal strings")
        
        # Check if public key already exists
        if cls.objects.filter(public_key=public_key).exists():
            raise ValueError("This public key is already in use")
        
        private_hash = hashlib.sha256(private_key.encode()).hexdigest()
        instance, _ = cls.objects.update_or_create(
            user=user,
            defaults={'public_key': public_key, 'private_key_hash': private_hash}
        )
        return public_key, private_key

class UserProfile(models.Model):
    """
    User profile information stored in the default database.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
