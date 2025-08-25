from rest_framework import serializers
from .models import Router, Package
from django.contrib.auth.models import User

class PackageSerializer(serializers.ModelSerializer):
    """Serializer for Package model"""
    router_name = serializers.CharField(source='router.name', read_only=True)
    package_type_display = serializers.CharField(source='get_package_type_display', read_only=True)
    duration_display = serializers.CharField(read_only=True)
    download_speed_display = serializers.CharField(read_only=True)
    upload_speed_display = serializers.CharField(read_only=True)
    speed_display = serializers.CharField(read_only=True)
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'router', 'router_name', 'package_type', 'package_type_display',
            'duration_hours', 'duration_display', 'price', 'download_speed_mbps',
            'upload_speed_mbps', 'download_speed_display', 'upload_speed_display',
            'speed_display', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'router_name', 'package_type_display', 'duration_display',
                           'download_speed_display', 'upload_speed_display', 'speed_display',
                           'created_at', 'updated_at']
    
    def validate(self, data):
        """Validate package data"""
        # Ensure package name is unique per router
        if 'name' in data and 'router' in data:
            existing_package = Package.objects.filter(
                router=data['router'],
                name=data['name']
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_package.exists():
                raise serializers.ValidationError(
                    f"A package with name '{data['name']}' already exists for this router."
                )
        
        # Validate price
        if 'price' in data and data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        
        # Validate speeds
        if 'download_speed_mbps' in data and data['download_speed_mbps'] <= 0:
            raise serializers.ValidationError("Download speed must be greater than 0.")
        
        if 'upload_speed_mbps' in data and data['upload_speed_mbps'] <= 0:
            raise serializers.ValidationError("Upload speed must be greater than 0.")
        
        # Validate duration
        if 'duration_hours' in data and data['duration_hours'] <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        
        return data

class RouterSerializer(serializers.ModelSerializer):
    """Serializer for Router model"""
    is_online = serializers.ReadOnlyField()
    last_checked = serializers.ReadOnlyField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Router
        fields = [
            'id', 'name', 'host', 'port', 'username', 'password', 
            'use_https', 'is_online', 'last_checked', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_online', 'last_checked', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Extract password and set it using the model's set_password method
        password = validated_data.pop('password', None)
        
        # Get any extra kwargs (like user) that were passed to save()
        extra_kwargs = {}
        for key in list(validated_data.keys()):
            if key not in self.Meta.fields:
                extra_kwargs[key] = validated_data.pop(key)
        
        router = Router(**validated_data)
        
        # Set the user if provided
        if 'user' in extra_kwargs:
            router.user = extra_kwargs['user']
        
        # Set password if provided
        if password:
            router.set_password(password)
        
        # Save the router to get an ID
        router.save()
        return router
    
    def update(self, instance, validated_data):
        # Handle password update if provided
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
