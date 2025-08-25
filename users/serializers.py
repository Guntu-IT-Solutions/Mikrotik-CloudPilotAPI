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

