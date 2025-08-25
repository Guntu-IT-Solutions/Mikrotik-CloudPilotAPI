from django.conf import settings
from .models import PaymentCredentials
from intasend import APIService


class IntaSendAPI:
    """IntaSend API integration class using official SDK"""
    
    def __init__(self, user):
        """
        Initialize IntaSend API with user
        
        Args:
            user: User instance to get credentials for
        """
        self.user = user
        self.credentials = self._get_latest_credentials()
        
        if not self.credentials:
            raise ValueError("No active IntaSend credentials found for this user")
        
        # Validate credentials
        if not self.credentials.api_key:
            raise ValueError("IntaSend API key is missing")
        
        if not self.credentials.encrypted_private_key:
            raise ValueError("IntaSend private key is missing")
        
        try:
            self.secret_key = self.credentials.get_private_key()
            if not self.secret_key:
                raise ValueError("Failed to decrypt IntaSend private key")
        except Exception as e:
            raise ValueError(f"Failed to decrypt IntaSend private key: {str(e)}")
        
        self.api_key = self.credentials.api_key
        self.sandbox = self.credentials.environment == 'sandbox'
        
        # Initialize IntaSend SDK service
        self.service = APIService(
            token=self.secret_key,
            publishable_key=self.api_key,
            test=self.sandbox
        )
        
        # Test API connectivity
        self._test_api_connection()
    
    def _test_api_connection(self):
        """Test if we can connect to IntaSend API using SDK"""
        try:
            # Test SDK initialization
            if self.service:
                # Test a simple API call to verify connectivity
                try:
                    # Try to get payment requests (this will test authentication)
                    response = self.service.collect.get_payment_requests()
                    # If we get here, connection is successful
                    pass
                except Exception as e:
                    # Connection test failed, but don't raise error
                    pass
                    
        except Exception as e:
            # Connection test failed, but don't raise error
            pass
    
    def _get_latest_credentials(self):
        """Get the latest active IntaSend credentials for the user"""
        try:
            return PaymentCredentials.objects.filter(
                user=self.user,
                provider='instasend',
                is_active=True
            ).latest('created_at')
        except PaymentCredentials.DoesNotExist:
            return None
    
    def create_payment_link(self, payment):
        """Create a payment link for the given payment using IntaSend SDK"""
        try:
            # Format phone number for IntaSend
            phone_number = self._format_phone_number(payment.phone_number)
            
            # Use IntaSend SDK to create payment link
            response = self.service.collect.payment_link(
                amount=float(payment.amount),
                currency=payment.currency,
                payment_method=payment.payment_method,
                phone_number=phone_number,
                first_name="WiFi",
                last_name="User",
                email=f"wifi-{payment.phone_number}@guntu.net",
                reference=str(payment.id),
                callback_url=self._get_callback_url(),
                success_url=self._get_success_url(payment.id),
                fail_url=self._get_fail_url(payment.id),
                metadata={
                    "payment_id": str(payment.id),
                    "package_name": payment.package.name,
                    "router_name": payment.router.name,
                    "mac_address": payment.mac_address,
                    "ip_address": payment.ip_address
                }
            )
            
            # Extract response data from the SDK response
            if hasattr(response, 'id'):
                payment.intasend_invoice_id = response.id
            if hasattr(response, 'state'):
                payment.intasend_state = response.state
            if hasattr(response, 'url'):
                payment.save()
            
            return {
                'success': True,
                'payment_url': getattr(response, 'url', None),
                'invoice_id': getattr(response, 'id', None),
                'state': getattr(response, 'state', 'PENDING')
            }
                
        except Exception as e:
            print(f"Error creating payment link: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def initiate_stk_push(self, payment):
        """Initiate M-Pesa STK push payment using IntaSend SDK"""
        try:
            # Format phone number for IntaSend
            phone_number = self._format_phone_number(payment.phone_number)
            
            # Use IntaSend SDK to initiate STK push
            response = self.service.collect.mpesa_stk_push(
                phone_number=phone_number,
                email=f"wifi-{payment.phone_number}@guntu.net",
                amount=float(payment.amount),
                narrative=f"WiFi Package: {payment.package.name}",
            )
            
            # Extract response data from the dictionary response
            if isinstance(response, dict):
                # Handle dictionary response
                if 'id' in response:
                    payment.intasend_payment_id = response['id']
                
                # Extract invoice details from the nested invoice object
                if 'invoice' in response and response['invoice']:
                    invoice = response['invoice']
                    if 'invoice_id' in invoice:
                        payment.intasend_invoice_id = invoice['invoice_id']
                    if 'state' in invoice:
                        payment.intasend_state = invoice['state']
                    if 'mpesa_reference' in invoice:
                        pass # No print statement here
                    if 'net_amount' in invoice:
                        pass # No print statement here
            else:
                # Handle object response (fallback)
                if hasattr(response, 'id'):
                    payment.intasend_payment_id = response.id
                
                if hasattr(response, 'invoice') and response.invoice:
                    invoice = response.invoice
                    if hasattr(invoice, 'invoice_id'):
                        payment.intasend_invoice_id = invoice.invoice_id
                    if hasattr(invoice, 'state'):
                        payment.intasend_state = invoice.state
            
            payment.status = 'processing'
            payment.save()
            
            # Return the extracted data
            invoice_id = None
            if isinstance(response, dict) and 'invoice' in response and response['invoice']:
                invoice_id = response['invoice'].get('invoice_id')
            elif hasattr(response, 'invoice') and response.invoice:
                invoice_id = getattr(response.invoice, 'invoice_id', None)
            
            return {
                'success': True,
                'payment_id': response.get('id') if isinstance(response, dict) else getattr(response, 'id', None),
                'invoice_id': invoice_id,
                'state': response.get('invoice', {}).get('state', 'PENDING') if isinstance(response, dict) else getattr(response.invoice, 'state', 'PENDING') if hasattr(response, 'invoice') and response.invoice else 'PENDING',
                'message': 'STK push sent successfully'
            }
                
        except Exception as e:
            print(f"Error initiating STK push: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, payment):
        """Check the status of a payment using IntaSend SDK"""
        try:
            # Check if payment is already completed or failed
            if payment.status in ['completed', 'failed', 'cancelled']:
                print(f"Payment {payment.id} is already {payment.status}, skipping API call")
                return {
                    'success': True,
                    'state': payment.intasend_state or 'UNKNOWN',
                    'status': payment.status,
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'message': f'Payment already {payment.status}'
                }
            
            # Only call IntaSend API if we have the necessary IDs and payment is still pending
            if not payment.intasend_payment_id and not payment.intasend_invoice_id:
                return {
                    'success': False,
                    'error': 'No IntaSend payment ID or invoice ID found'
                }
            
            if payment.intasend_invoice_id:
                response = self.service.collect.status(invoice_id=payment.intasend_invoice_id)
            elif payment.intasend_payment_id:
                response = self.service.collect.get_payment_request(payment.intasend_payment_id)
            else:
                return {
                    'success': False,
                    'error': 'No IntaSend payment ID or invoice ID found'
                }
            
            # Extract response data from the response
            if isinstance(response, dict):
                # Handle dictionary response from status method
                if 'invoice' in response and response['invoice']:
                    invoice = response['invoice']
                    
                    state = invoice.get('state', 'UNKNOWN')
                    amount = invoice.get('net_amount')
                    currency = invoice.get('currency')
                    
                    return {
                        'success': True,
                        'state': state,
                        'status': state,
                        'amount': amount,
                        'currency': currency,
                        'mpesa_reference': invoice.get('api_ref'),
                        'failed_reason': invoice.get('failed_reason'),
                        'provider': invoice.get('provider'),
                        'charges': invoice.get('charges')
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No invoice data in response'
                    }
            elif hasattr(response, 'invoice') and response.invoice:
                # Handle object response (fallback)
                invoice = response.invoice
                return {
                    'success': True,
                    'state': getattr(invoice, 'state', 'UNKNOWN'),
                    'status': getattr(invoice, 'state', 'UNKNOWN'),
                    'amount': getattr(invoice, 'net_amount', None),
                    'currency': getattr(invoice, 'currency', None),
                    'mpesa_reference': getattr(invoice, 'api_ref', None),
                    'failed_reason': getattr(invoice, 'failed_reason', None),
                    'provider': getattr(invoice, 'provider', None),
                    'charges': getattr(invoice, 'charges', None)
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid response structure from IntaSend SDK'
                }
                
        except Exception as e:
            print(f"Error checking payment status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _format_phone_number(self, phone_number):
        """Format phone number for IntaSend API"""
        # Remove any non-digit characters
        digits_only = ''.join(filter(str.isdigit, phone_number))
        
        # If it starts with 0, replace with 254
        if digits_only.startswith('0'):
            digits_only = '254' + digits_only[1:]
        
        # If it doesn't start with 254, add it
        if not digits_only.startswith('254'):
            digits_only = '254' + digits_only
        
        return digits_only
    
    def _get_callback_url(self):
        """Get the webhook callback URL"""
        # First check if custom callback URL is set in settings
        if hasattr(settings, 'INTASEND_CALLBACK_URL'):
            return settings.INTASEND_CALLBACK_URL
        
        try:
            from django.contrib.sites.models import Site
            site = Site.objects.get_current()
            return f"https://{site.domain}/api/payments/webhook/"
        except (ImportError, Exception):
            # Fallback to a generic webhook URL
            return "https://yourdomain.com/api/payments/webhook/"
    
    def _get_success_url(self, payment_id):
        """Get the success URL"""
        # First check if custom success URL base is set in settings
        if hasattr(settings, 'INTASEND_SUCCESS_URL_BASE'):
            return f"{settings.INTASEND_SUCCESS_URL_BASE}{payment_id}/"
        
        try:
            from django.contrib.sites.models import Site
            site = Site.objects.get_current()
            return f"https://{site.domain}/payment/success/{payment_id}/"
        except (ImportError, Exception):
            # Fallback to a generic success URL
            return f"https://yourdomain.com/payment/success/{payment_id}/"
    
    def _get_fail_url(self, payment_id):
        """Get the failure URL"""
        # First check if custom failure URL base is set in settings
        if hasattr(settings, 'INTASEND_FAIL_URL_BASE'):
            return f"{settings.INTASEND_FAIL_URL_BASE}{payment_id}/"
        
        try:
            from django.contrib.sites.models import Site
            site = Site.objects.get_current()
            return f"https://{site.domain}/payment/failed/{payment_id}/"
        except (ImportError, Exception):
            # Fallback to a generic failure URL
            return f"https://yourdomain.com/payment/failed/{payment_id}/"
