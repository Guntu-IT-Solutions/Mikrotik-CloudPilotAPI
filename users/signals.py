from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import APIKey

@receiver(post_save, sender=User)
def create_user_api_keys(sender, instance, created, **kwargs):
    """Automatically create API keys when a new user is created."""
    if created:
        APIKey.create_for_user(instance)