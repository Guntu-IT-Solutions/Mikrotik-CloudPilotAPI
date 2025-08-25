from rest_framework import serializers
from .models import PaymentCredentials, Payment

class PaymentCredentialsSerializer(serializers.ModelSerializer):
    """Serializer for PaymentCredentials model"""
    
    provider_display = serializers.CharField(source='get_provider_display_name', read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    is_sandbox = serializers.BooleanField(read_only=True)
    private_key = serializers.CharField(write_only=True, required=True, max_length=255)
    
    class Meta:
        model = PaymentCredentials
        fields = [
            'id', 'provider', 'provider_display', 'api_key', 'private_key',
            'environment', 'is_active', 'created_at', 'updated_at',
            'is_live', 'is_sandbox'
        ]
        read_only_fields = ['id', 'provider_display', 'encrypted_private_key', 'private_key_hash', 'created_at', 'updated_at', 'is_live', 'is_sandbox']
        extra_kwargs = {
            'api_key': {'required': True},
            'provider': {'required': True},
        }
    
    def get_fields(self):
        """Override to handle private_key field properly"""
        fields = super().get_fields()
        # Ensure private_key is not treated as a model field
        if 'private_key' in fields:
            fields['private_key'].source = None
        return fields
    
    def validate(self, data):
        """Validate payment credentials data"""
        provider = data.get('provider')
        api_key = data.get('api_key')
        private_key = data.get('private_key')
        environment = data.get('environment', 'sandbox')
        
        # Check if user already has credentials for this provider
        user = self.context['request'].user
        existing_credentials = PaymentCredentials.objects.filter(
            user=user, 
            provider=provider
        ).first()
        
        if existing_credentials and self.instance != existing_credentials:
            raise serializers.ValidationError(
                f"You already have credentials for {provider}. Update existing credentials instead."
            )
        
        # Validate API key format (basic validation)
        if api_key and len(api_key.strip()) < 10:
            raise serializers.ValidationError("API key must be at least 10 characters long")
        
        # Validate private key format (basic validation)
        if private_key and len(private_key.strip()) < 10:
            raise serializers.ValidationError("Private key must be at least 10 characters long")
        
        return data
    
    def create(self, validated_data):
        """Create new payment credentials with encrypted private key"""
        private_key = validated_data.pop('private_key')
        validated_data['user'] = self.context['request'].user
        
        # Create instance without saving
        credentials = PaymentCredentials(**validated_data)
        
        # Set encrypted private key
        credentials.set_private_key(private_key)
        
        # Save the instance
        credentials.save()
        return credentials

class PaymentCredentialsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating PaymentCredentials (without private key)"""
    
    provider_display = serializers.CharField(source='get_provider_display_name', read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    is_sandbox = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PaymentCredentials
        fields = [
            'id', 'provider', 'provider_display', 'api_key', 'environment',
            'is_active', 'created_at', 'updated_at', 'is_live', 'is_sandbox'
        ]
        read_only_fields = ['id', 'provider', 'provider_display', 'created_at', 'updated_at', 'is_live', 'is_sandbox']
    
    def validate(self, data):
        """Validate update data"""
        api_key = data.get('api_key')
        
        if api_key and len(api_key.strip()) < 10:
            raise serializers.ValidationError("API key must be at least 10 characters long")
        
        return data

class PaymentCredentialsListSerializer(serializers.ModelSerializer):
    """Serializer for listing PaymentCredentials (without sensitive data)"""
    
    provider_display = serializers.CharField(source='get_provider_display_name', read_only=True)
    is_live = serializers.BooleanField(read_only=True)
    is_sandbox = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PaymentCredentials
        fields = [
            'id', 'provider', 'provider_display', 'environment',
            'is_active', 'created_at', 'updated_at', 'is_live', 'is_sandbox'
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'router', 'package', 'phone_number', 'amount', 'currency',
            'payment_method', 'payment_method_display', 'status', 'status_display',
            'intasend_invoice_id', 'intasend_payment_id', 'intasend_state',
            'mac_address', 'ip_address', 'package_expiry_time', 'created_at', 
            'updated_at', 'completed_at', 'error_message', 'retry_count', 
            'is_successful', 'is_failed', 'is_pending', 'is_expired', 'is_active'
        ]
        read_only_fields = [
            'id', 'status_display', 'payment_method_display', 'intasend_invoice_id',
            'intasend_payment_id', 'intasend_state', 'package_expiry_time', 'created_at', 
            'updated_at', 'completed_at', 'error_message', 'retry_count', 
            'is_successful', 'is_failed', 'is_pending', 'is_expired', 'is_active'
        ]
        extra_kwargs = {
            'user': {'required': False},  # Can be null/blank
            'router': {'required': True},
            'package': {'required': True},
            'phone_number': {'required': True},
            'amount': {'required': True},
            'currency': {'required': False},
            'payment_method': {'required': False},
            'mac_address': {'required': False},
            'ip_address': {'required': False},
        }
    
    def validate(self, data):
        """Validate payment data"""
        amount = data.get('amount')
        phone_number = data.get('phone_number')
        package = data.get('package')
        router = data.get('router')
        
        # Validate amount
        if amount and amount <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        
        # Validate phone number format (basic validation for East Africa)
        if phone_number:
            # Remove any non-digit characters
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if len(clean_phone) < 9 or len(clean_phone) > 12:
                raise serializers.ValidationError("Invalid phone number format")
        
        # Validate package
        if package and not package.is_active:
            raise serializers.ValidationError("Selected package is not active")
        
        # Validate that package belongs to the selected router
        if package and router and package.router != router:
            raise serializers.ValidationError("Package must belong to the selected router")
        
        return data
    
    def create(self, validated_data):
        """Create new payment"""
        # Set user from request context if not provided
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        
        # Set default currency if not provided
        if 'currency' not in validated_data:
            validated_data['currency'] = 'KES'
        
        # Set default payment method if not provided
        if 'payment_method' not in validated_data:
            validated_data['payment_method'] = 'mpesa'
        
        return super().create(validated_data)


class PaymentListSerializer(serializers.ModelSerializer):
    """Serializer for listing Payment transactions (without sensitive data)"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    is_successful = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'phone_number', 'amount', 'currency', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'created_at', 'updated_at', 'completed_at',
            'is_successful', 'is_failed', 'is_pending'
        ]
        read_only_fields = fields


class PaymentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating Payment status and IntaSend fields"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'status', 'status_display', 'intasend_invoice_id', 'intasend_payment_id',
            'intasend_state', 'error_message', 'retry_count', 'payment_method_display'
        ]
        read_only_fields = [
            'id', 'status_display', 'payment_method_display', 'created_at', 'updated_at'
        ]
    
    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:
            current_status = self.instance.status
            # Only allow certain status transitions
            if current_status == 'completed' and value != 'completed':
                raise serializers.ValidationError("Cannot change status of completed payment")
            if current_status == 'cancelled' and value != 'cancelled':
                raise serializers.ValidationError("Cannot change status of cancelled payment")
        
        return value
