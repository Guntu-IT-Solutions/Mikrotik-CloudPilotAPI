from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib
import uuid

# Create your models here.

class PaymentCredentials(models.Model):
    """Store user payment API credentials for different payment providers"""
    
    PAYMENT_PROVIDERS = [
        ('kopokopo', 'KopoKopo'),
        ('instasend', 'InstaSend'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_credentials')
    provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDERS)
    api_key = models.CharField(max_length=255, help_text="Public API key for the payment provider")
    encrypted_private_key = models.BinaryField(help_text="Encrypted private key for the payment provider", null=True, blank=True)
    private_key_hash = models.CharField(max_length=64, help_text="SHA-256 hash of the private key for verification", null=True, blank=True)
    environment = models.CharField(max_length=10, choices=[('sandbox', 'Sandbox'), ('live', 'Live')], default='sandbox')
    is_active = models.BooleanField(default=True, help_text="Whether these credentials are currently active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'provider']
        ordering = ['-created_at']
        verbose_name = "Payment Credential"
        verbose_name_plural = "Payment Credentials"
    
    def __str__(self):
        return f"{self.user.username} - {self.provider} ({self.environment})"
    
    def _get_fernet(self):
        """Get Fernet instance for encryption/decryption"""
        try:
            return Fernet(settings.ENCRYPTION_KEY)
        except Exception as e:
            raise ValueError(f"Invalid encryption key: {e}")
    
    def set_private_key(self, private_key):
        """Encrypt and store the private key"""
        if not private_key:
            raise ValueError("Private key cannot be empty")
        
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(private_key.encode())
        self.encrypted_private_key = encrypted_data
        
        # Also store hash for verification
        self.private_key_hash = hashlib.sha256(private_key.encode()).hexdigest()
    
    def get_private_key(self):
        """Decrypt and return the private key"""
        if not self.encrypted_private_key:
            return None
        
        try:
            fernet = self._get_fernet()
            decrypted_data = fernet.decrypt(self.encrypted_private_key)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt private key: {e}")
    
    def save(self, *args, **kwargs):
        """Handle private key encryption before saving"""
        super().save(*args, **kwargs)
    
    def verify_private_key(self, private_key):
        """Verify if the provided private key matches the stored hash"""
        if not self.private_key_hash:
            return False
        return hashlib.sha256(private_key.encode()).hexdigest() == self.private_key_hash
    
    def get_provider_display_name(self):
        """Get human-readable provider name"""
        return dict(self.PAYMENT_PROVIDERS)[self.provider]
    
    def is_live(self):
        """Check if credentials are for live environment"""
        return self.environment == 'live'
    
    def is_sandbox(self):
        """Check if credentials are for sandbox environment"""
        return self.environment == 'sandbox'


class Payment(models.Model):
    """Payment model for IntaSend transactions"""
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    ]
    
    PAYMENT_PROVIDERS = [
        ('kopokopo', 'KopoKopo'),
        ('instasend', 'IntaSend'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    router = models.ForeignKey('routers.Router', on_delete=models.CASCADE, related_name='payments', help_text="Router this payment is for")
    package = models.ForeignKey('routers.Package', on_delete=models.CASCADE, related_name='payments')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='mpesa')
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDERS, default='instasend', help_text="Payment provider used (KopoKopo, IntaSend)")
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    
    # IntaSend specific fields
    intasend_invoice_id = models.CharField(max_length=100, blank=True)
    intasend_payment_id = models.CharField(max_length=100, blank=True)
    intasend_state = models.CharField(max_length=50, blank=True)
    
    # Device information
    mac_address = models.CharField(max_length=17, blank=True)
    ip_address = models.CharField(max_length=45, blank=True)
    
    # Package expiry time (calculated from package duration)
    package_expiry_time = models.DateTimeField(null=True, blank=True, help_text="When the package access expires")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['intasend_payment_id']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['package_expiry_time']),
            models.Index(fields=['router', 'status']),
        ]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
    
    def __str__(self):
        return f"Payment {self.id} - {self.router.name} - {self.phone_number} - {self.status}"
    
    def clean(self):
        """Validate that package belongs to the selected router"""
        from django.core.exceptions import ValidationError
        if self.package and self.router and self.package.router != self.router:
            raise ValidationError("Package must belong to the selected router")
    
    @property
    def is_successful(self):
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        return self.status in ['failed', 'cancelled']
    
    @property
    def is_pending(self):
        return self.status in ['pending', 'processing']
    
    @property
    def is_expired(self):
        """Check if the package access has expired"""
        if not self.package_expiry_time:
            return False
        from django.utils import timezone
        return timezone.now() > self.package_expiry_time
    
    @property
    def is_active(self):
        """Check if the package access is still active"""
        return self.is_successful and not self.is_expired
    
    def calculate_expiry_time(self):
        """Calculate package expiry time based on package duration"""
        if not self.package or not self.completed_at:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate expiry time based on package duration in hours
        expiry_time = self.completed_at + timedelta(hours=self.package.duration_hours)
        return expiry_time
    
    def mark_completed(self):
        """Mark payment as completed and calculate expiry time"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.package_expiry_time = self.calculate_expiry_time()
        self.save()
    
    def mark_failed(self, error_message=""):
        """Mark payment as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.save()
