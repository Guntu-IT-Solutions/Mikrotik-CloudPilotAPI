from django.contrib.auth.models import User
from rest_framework import serializers
from .models import APIKey


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        # Create the user (database creation is handled in signals/views)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['public_key', 'created_at']
        read_only_fields = fields

class CustomAPIKeySerializer(serializers.Serializer):
    public_key = serializers.CharField(max_length=64, min_length=64)
    private_key = serializers.CharField(max_length=128, min_length=128)
    
    def validate_public_key(self, value):
        """Validate public key format"""
        if len(value) != 64:
            raise serializers.ValidationError("Public key must be exactly 64 characters")
        
        # Check if it's valid hex
        try:
            int(value, 16)
        except ValueError:
            raise serializers.ValidationError("Public key must be a valid hexadecimal string")
        
        # Check if it's already in use
        if APIKey.objects.filter(public_key=value).exists():
            raise serializers.ValidationError("This public key is already in use")
        
        return value
    
    def validate_private_key(self, value):
        """Validate private key format"""
        if len(value) != 128:
            raise serializers.ValidationError("Private key must be exactly 128 characters")
        
        # Check if it's valid hex
        try:
            int(value, 16)
        except ValueError:
            raise serializers.ValidationError("Private key must be a valid hexadecimal string")
        
        return value

