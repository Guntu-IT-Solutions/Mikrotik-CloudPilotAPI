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
