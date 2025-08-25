from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentCredentials, Payment

@admin.register(PaymentCredentials)
class PaymentCredentialsAdmin(admin.ModelAdmin):
    """Admin interface for PaymentCredentials model"""
    
    list_display = [
        'user', 'provider', 'environment', 'is_active', 'created_at', 'updated_at'
    ]
    
    list_filter = [
        'provider', 'environment', 'is_active', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'provider', 'api_key'
    ]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Provider Details', {
            'fields': ('provider', 'environment', 'is_active')
        }),
        ('API Credentials', {
            'fields': ('api_key',)
        }),
        ('Security & Metadata', {
            'fields': ('encrypted_private_key_display', 'private_key_hash_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'encrypted_private_key_display', 'private_key_hash_display', 'created_at', 'updated_at'
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with user information"""
        return super().get_queryset(request).select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete payment credentials"""
        return request.user.is_superuser
    
    def encrypted_private_key_display(self, obj):
        """Display encrypted private key in a readable format"""
        if obj.encrypted_private_key:
            # Show first 20 characters of encrypted data
            encrypted_str = str(obj.encrypted_private_key[:20])
            return format_html(
                '<code style="background: #f0f0f0; padding: 2px 4px; border-radius: 3px;">{}</code>...',
                encrypted_str
            )
        return 'No private key'
    
    encrypted_private_key_display.short_description = 'Encrypted Private Key (Preview)'
    
    def private_key_hash_display(self, obj):
        """Display private key hash in a readable format"""
        if obj.private_key_hash:
            return format_html(
                '<code style="background: #f0f0f0; padding: 2px 4px; border-radius: 3px;">{}</code>',
                obj.private_key_hash[:16] + '...'
            )
        return 'No hash'
    
    private_key_hash_display.short_description = 'Private Key Hash (Preview)'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""
    
    list_display = [
        'id', 'user', 'router', 'package', 'phone_number', 'amount', 'currency', 'payment_method', 
        'status', 'created_at', 'package_expiry_time', 'is_successful', 'is_failed', 'is_expired'
    ]
    
    list_filter = [
        'router', 'status', 'payment_method', 'currency', 'created_at', 'completed_at', 'package_expiry_time'
    ]
    
    search_fields = [
        'id', 'user__username', 'router__name', 'phone_number', 'intasend_payment_id', 'intasend_invoice_id', 'package__name'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'completed_at', 'package_expiry_time', 
        'is_successful', 'is_failed', 'is_pending', 'is_expired', 'is_active'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'router', 'package', 'phone_number', 'amount', 'currency')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'status', 'created_at', 'updated_at', 'completed_at')
        }),
        ('Package Access', {
            'fields': ('package_expiry_time', 'is_expired', 'is_active'),
            'classes': ('collapse',)
        }),
        ('IntaSend Integration', {
            'fields': ('intasend_invoice_id', 'intasend_payment_id', 'intasend_state'),
            'classes': ('collapse',)
        }),
        ('Device Information', {
            'fields': ('mac_address', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Error Tracking', {
            'fields': ('error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
        ('Computed Properties', {
            'fields': ('is_successful', 'is_failed', 'is_pending'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related information"""
        return super().get_queryset(request).select_related('user', 'package', 'router')
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete payments"""
        return request.user.is_superuser
    
    def is_successful(self, obj):
        """Display success status"""
        return obj.is_successful
    
    is_successful.boolean = True
    is_successful.short_description = 'Successful'
    
    def is_failed(self, obj):
        """Display failed status"""
        return obj.is_failed
    
    is_failed.boolean = True
    is_failed.short_description = 'Failed'
    
    def is_expired(self, obj):
        """Display expired status"""
        return obj.is_expired
    
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
