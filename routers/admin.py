from django.contrib import admin
from .models import Router, Package

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    """Admin interface for Package model"""
    
    list_display = [
        'name', 'router', 'package_type', 'duration_display', 'price', 
        'download_speed_display', 'upload_speed_display', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'router', 'package_type', 'is_active', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'name', 'description', 'router__name'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'duration_display', 'download_speed_display', 
        'upload_speed_display', 'speed_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'router', 'package_type', 'description', 'is_active')
        }),
        ('Package Details', {
            'fields': ('duration_hours', 'price')
        }),
        ('Speed Limits', {
            'fields': ('download_speed_mbps', 'upload_speed_mbps', 'download_speed_display', 'upload_speed_display', 'speed_display')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display duration in admin"""
        return obj.duration_display
    
    duration_display.short_description = 'Duration'
    
    def download_speed_display(self, obj):
        """Display download speed in admin"""
        return obj.download_speed_display
    
    download_speed_display.short_description = 'Download Speed'
    
    def upload_speed_display(self, obj):
        """Display upload speed in admin"""
        return obj.upload_speed_display
    
    upload_speed_display.short_description = 'Upload Speed'
    
    def speed_display(self, obj):
        """Display combined speed in admin"""
        return obj.speed_display
    
    speed_display.short_description = 'Speed (Down/Up)'


@admin.register(Router)
class RouterAdmin(admin.ModelAdmin):
    """Admin interface for Router model"""
    
    list_display = [
        'name', 'user', 'host', 'port', 'username', 'use_https', 'is_online', 'last_checked'
    ]
    
    list_filter = [
        'use_https', 'is_online', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'name', 'host', 'username', 'user__username'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'last_checked'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'host', 'port')
        }),
        ('Authentication', {
            'fields': ('username', 'encrypted_password', 'use_https')
        }),
        ('Status', {
            'fields': ('is_online', 'last_checked')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with user information"""
        return super().get_queryset(request).select_related('user')
