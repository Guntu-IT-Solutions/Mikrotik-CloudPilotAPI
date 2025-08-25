from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal
import base64

class Router(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routers')
    name = models.CharField(max_length=100)
    host = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$|^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$',
                message='Enter a valid IP address or domain name.'
            )
        ],
        help_text="IP address or domain name of the router"
    )
    port = models.PositiveIntegerField(default=80)
    username = models.CharField(max_length=50)
    encrypted_password = models.BinaryField()
    use_https = models.BooleanField(default=False)
    last_checked = models.DateTimeField(null=True, blank=True)
    is_online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.host})"

    def set_password(self, password):
        """Encrypt and store the password"""
        if not hasattr(settings, 'ENCRYPTION_KEY'):
            raise ValueError("ENCRYPTION_KEY not configured in settings")
        
        fernet = Fernet(settings.ENCRYPTION_KEY)
        self.encrypted_password = fernet.encrypt(password.encode())

    def get_password(self):
        """Decrypt and return the password for use in connections"""
        if not hasattr(settings, 'ENCRYPTION_KEY'):
            raise ValueError("ENCRYPTION_KEY not configured in settings")
        
        fernet = Fernet(settings.ENCRYPTION_KEY)
        return fernet.decrypt(self.encrypted_password).decode()

    @property
    def base_url(self):
        """Get the base URL for API requests"""
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}/rest"

    def save(self, *args, **kwargs):
        # If encrypted_password is not set but we have a plain password in kwargs
        if not self.encrypted_password and 'password' in kwargs:
            self.set_password(kwargs.pop('password'))
        
        super().save(*args, **kwargs)


class Package(models.Model):
    """WiFi package model for different durations and speeds"""
    
    PACKAGE_TYPES = [
        ('hourly', 'Hourly Package'),
        ('monthly', 'Monthly Package'),
    ]
    
    name = models.CharField(max_length=100)
    router = models.ForeignKey(Router, on_delete=models.CASCADE, related_name='packages', help_text="Router this package applies to")
    package_type = models.CharField(max_length=10, choices=PACKAGE_TYPES)
    duration_hours = models.PositiveIntegerField(help_text="Duration in hours")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    download_speed_mbps = models.PositiveIntegerField(help_text="Download speed limit in Mbps")
    upload_speed_mbps = models.PositiveIntegerField(help_text="Upload speed limit in Mbps")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['router', 'package_type', 'price']
        verbose_name = "WiFi Package"
        verbose_name_plural = "WiFi Packages"
        unique_together = ['router', 'name']  # Package names must be unique per router
    
    def __str__(self):
        return f"{self.router.name} - {self.name} - {self.get_package_type_display()} - ${self.price}"
    
    @property
    def duration_display(self):
        """Return human readable duration"""
        if self.package_type == 'hourly':
            if self.duration_hours == 1:
                return "1 hour"
            return f"{self.duration_hours} hours"
        else:
            months = self.duration_hours // 720  # 30 days * 24 hours
            return f"{months} month{'s' if months != 1 else ''}"
    
    @property
    def download_speed_display(self):
        """Return human readable download speed"""
        if self.download_speed_mbps >= 1000:
            return f"{self.download_speed_mbps/1000:.1f} Gbps"
        return f"{self.download_speed_mbps} Mbps"
    
    @property
    def upload_speed_display(self):
        """Return human readable upload speed"""
        if self.upload_speed_mbps >= 1000:
            return f"{self.upload_speed_mbps/1000:.1f} Gbps"
        return f"{self.upload_speed_mbps} Mbps"
    
    @property
    def speed_display(self):
        """Return combined speed display (for backward compatibility)"""
        return f"{self.download_speed_display} / {self.upload_speed_display}"
