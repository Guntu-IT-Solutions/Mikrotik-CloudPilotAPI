from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render
from django.http import HttpResponse
from .models import PaymentCredentials, Payment
from .serializers import (
    PaymentCredentialsSerializer, 
    PaymentCredentialsUpdateSerializer,
    PaymentCredentialsListSerializer,
    PaymentSerializer,
    PaymentListSerializer,
    PaymentUpdateSerializer
)
from .intasend_api import IntaSendAPI
from .authentication import PublicKeyAuthentication

# Create your views here.

# Payment Credentials Views

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_credentials_list(request):
    """List all payment credentials for the authenticated user or create new ones."""
    if request.method == 'GET':
        credentials = PaymentCredentials.objects.filter(user=request.user)
        serializer = PaymentCredentialsListSerializer(credentials, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PaymentCredentialsSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            credentials = serializer.save()
            # Return the created credentials without private key
            response_serializer = PaymentCredentialsListSerializer(credentials)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_credentials_detail(request, pk):
    """Retrieve, update or delete payment credentials."""
    try:
        credentials = PaymentCredentials.objects.get(pk=pk, user=request.user)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': 'Payment credentials not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentCredentialsListSerializer(credentials)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PaymentCredentialsUpdateSerializer(credentials, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PaymentCredentialsListSerializer(credentials)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        provider_name = credentials.get_provider_display_name()
        credentials.delete()
        return Response({
            'message': f'Payment credentials for {provider_name} have been successfully deleted'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_private_key(request, pk):
    """Update private key for existing payment credentials."""
    try:
        credentials = PaymentCredentials.objects.get(pk=pk, user=request.user)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': 'Payment credentials not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    private_key = request.data.get('private_key')
    if not private_key:
        return Response({
            'error': 'Private key is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(private_key.strip()) < 10:
        return Response({
            'error': 'Private key must be at least 10 characters long'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Update private key using the encrypted method
        credentials.set_private_key(private_key)
        credentials.save()
        
        response_serializer = PaymentCredentialsListSerializer(credentials)
        return Response({
            'message': 'Private key updated successfully',
            'credentials': response_serializer.data
        })
    except Exception as e:
        return Response({
            'error': f'Failed to update private key: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def verify_credentials(request, pk):
    """Verify payment credentials by checking private key."""
    try:
        credentials = PaymentCredentials.objects.get(pk=pk, user=request.user)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': 'Payment credentials not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    private_key = request.data.get('private_key')
    if not private_key:
        return Response({
            'error': 'Private key is required for verification'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    is_valid = credentials.verify_private_key(private_key)
    
    return Response({
        'credentials_id': pk,
        'provider': credentials.provider,
        'provider_display': credentials.get_provider_display_name(),
        'is_valid': is_valid,
        'message': 'Credentials verified successfully' if is_valid else 'Invalid private key'
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_credentials_by_provider(request, provider):
    """Get payment credentials for a specific provider."""
    try:
        credentials = PaymentCredentials.objects.get(user=request.user, provider=provider)
        serializer = PaymentCredentialsListSerializer(credentials)
        return Response(serializer.data)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': f'No credentials found for {provider}'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def toggle_credentials_status(request, pk):
    """Toggle the active status of payment credentials."""
    try:
        credentials = PaymentCredentials.objects.get(pk=pk, user=request.user)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': 'Payment credentials not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    credentials.is_active = not credentials.is_active
    credentials.save()
    
    status_text = 'activated' if credentials.is_active else 'deactivated'
    
    response_serializer = PaymentCredentialsListSerializer(credentials)
    return Response({
        'message': f'Payment credentials for {credentials.get_provider_display_name()} have been {status_text}',
        'credentials': response_serializer.data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_private_key(request, pk):
    """Get the decrypted private key for API usage."""
    try:
        credentials = PaymentCredentials.objects.get(pk=pk, user=request.user)
    except PaymentCredentials.DoesNotExist:
        return Response({
            'error': 'Payment credentials not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        private_key = credentials.get_private_key()
        return Response({
            'credentials_id': pk,
            'provider': credentials.provider,
            'provider_display': credentials.get_provider_display_name(),
            'private_key': private_key,
            'message': 'Private key retrieved successfully'
        })
    except Exception as e:
        return Response({
            'error': f'Failed to retrieve private key: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Payment Views

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_list(request):
    """List all payments for the authenticated user or create new ones."""
    if request.method == 'GET':
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PaymentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save()
            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_detail(request, pk):
    """Retrieve, update or delete payment."""
    try:
        payment = Payment.objects.get(pk=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PaymentUpdateSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        payment.delete()
        return Response({
            'message': f'Payment {pk} has been successfully deleted'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_payment_completed(request, pk):
    """Mark payment as completed."""
    try:
        payment = Payment.objects.get(pk=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    payment.mark_completed()
    response_serializer = PaymentSerializer(payment)
    return Response({
        'message': 'Payment marked as completed',
        'payment': response_serializer.data
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_payment_failed(request, pk):
    """Mark payment as failed."""
    try:
        payment = Payment.objects.get(pk=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    error_message = request.data.get('error_message', '')
    payment.mark_failed(error_message)
    response_serializer = PaymentSerializer(payment)
    return Response({
        'message': 'Payment marked as failed',
        'payment': response_serializer.data
    })

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def increment_payment_retry(request, pk):
    """Increment payment retry count."""
    try:
        payment = Payment.objects.get(pk=pk, user=request.user)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    payment.increment_retry()
    response_serializer = PaymentSerializer(payment)
    return Response({
        'message': 'Payment retry count incremented',
        'payment': response_serializer.data
    })

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_by_status(request, status):
    """Get payments by status for the authenticated user."""
    valid_statuses = [choice[0] for choice in Payment.PAYMENT_STATUS]
    if status not in valid_statuses:
        return Response({
            'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    payments = Payment.objects.filter(user=request.user, status=status)
    serializer = PaymentListSerializer(payments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def payment_by_method(request, method):
    """Get payments by payment method for the authenticated user."""
    valid_methods = [choice[0] for choice in Payment.PAYMENT_METHODS]
    if method not in valid_methods:
        return Response({
            'error': f'Invalid payment method. Must be one of: {", ".join(valid_methods)}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    payments = Payment.objects.filter(user=request.user, payment_method=method)
    serializer = PaymentListSerializer(payments, many=True)
    return Response(serializer.data)

# IntaSend Payment Views

@api_view(['POST'])
@authentication_classes([PublicKeyAuthentication])
@permission_classes([IsAuthenticated])
def initiate_intasend_payment(request):
    """Initiate IntaSend payment via STK push"""
    try:
        # Validate that we have a proper user (not AnonymousUser)
        if not request.user or request.user.is_anonymous:
            return Response({
                'error': 'Authentication required. Please provide a valid public API key in the X-Public-Key header.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get required data
        router_id = request.data.get('router_id')
        package_id = request.data.get('package_id')
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'mpesa')
        mac_address = request.data.get('mac_address', '')
        ip_address = request.data.get('ip_address', '')
        
        # Validate required fields
        if not all([router_id, package_id, phone_number, amount]):
            return Response({
                'error': 'router_id, package_id, phone_number, and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get router and package
        from routers.models import Router, Package
        try:
            router = Router.objects.get(pk=router_id, user=request.user)
        except Router.DoesNotExist:
            return Response({
                'error': 'Router not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            package = Package.objects.get(pk=package_id, router=router, is_active=True)
        except Package.DoesNotExist:
            return Response({
                'error': 'Package not found or not active for this router'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount matches package price
        if float(amount) != float(package.price):
            return Response({
                'error': f'Amount must match package price: {package.price} {package.currency}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            router=router,
            package=package,
            phone_number=phone_number,
            amount=amount,
            currency='KES',
            payment_method=payment_method,
            payment_provider='instasend',  # Set payment provider
            mac_address=mac_address,
            ip_address=ip_address,
            status='pending'
        )
        
        # Initialize IntaSend API with automatically fetched credentials
        intasend_api = IntaSendAPI(request.user)
        
        # Initiate STK push
        result = intasend_api.initiate_stk_push(payment)
        
        if result['success']:
            # Return payment details with IntaSend info
            response_serializer = PaymentSerializer(payment)
            return Response({
                'message': 'STK push initiated successfully',
                'payment': response_serializer.data,
                'intasend': {
                    'payment_id': result['payment_id'],
                    'invoice_id': result.get('invoice_id'),
                    'state': result['state'],
                    'message': result['message']
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # Mark payment as failed
            payment.status = 'failed'
            payment.error_message = result['error']
            payment.save()
            
            return Response({
                'error': f'Failed to initiate STK push: {result["error"]}',
                'payment_id': str(payment.id)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError as e:
        # Handle credential-related errors
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Payment initiation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([PublicKeyAuthentication])
@permission_classes([IsAuthenticated])
def check_intasend_payment_status(request, payment_id):
    """Check the status of an IntaSend payment"""
    try:
        # Validate that we have a proper user (not AnonymousUser)
        if not request.user or request.user.is_anonymous:
            return Response({
                'error': 'Authentication required. Please provide a valid public API key in the X-Public-Key header.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get payment
        try:
            payment = Payment.objects.get(pk=payment_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({
                'error': 'Payment not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if payment has IntaSend IDs and is from IntaSend
        if payment.payment_provider != 'instasend':
            return Response({
                'error': 'This payment was not initiated through IntaSend'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not payment.intasend_payment_id and not payment.intasend_invoice_id:
            return Response({
                'error': 'This payment was not initiated through IntaSend'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Initialize IntaSend API with automatically fetched credentials
        intasend_api = IntaSendAPI(request.user)
        
        # Check payment status
        result = intasend_api.check_payment_status(payment)
        
        if result['success']:
            # Update payment status based on IntaSend response
            intasend_state = result['state']
            
            # Update the IntaSend state first
            payment.intasend_state = intasend_state
            
            # Check for completed states (IntaSend uses "COMPLETE", not "COMPLETED")
            completed_states = ['COMPLETE', 'COMPLETED', 'SUCCESS', 'SUCCESSFUL']
            failed_states = ['FAILED', 'CANCELLED', 'DECLINED', 'ERROR']
            
            if intasend_state in completed_states:
                payment.status = 'completed'
                payment.mark_completed()
            elif intasend_state in failed_states:
                payment.status = 'failed'
                payment.error_message = f'Payment {intasend_state.lower()} on IntaSend'
                payment.save()
            else:
                # Keep current status but update IntaSend state
                payment.save()
            
            # Return simplified response for completed payments
            if intasend_state in completed_states:
                response_serializer = PaymentSerializer(payment)
                return Response({
                    'message': 'Payment completed successfully!',
                    'payment': response_serializer.data,
                    'status': 'completed',
                    'state': intasend_state
                })
            else:
                # Return detailed response for other states
                response_serializer = PaymentSerializer(payment)
                return Response({
                    'message': 'Payment status checked successfully',
                    'payment': response_serializer.data,
                    'status': payment.status,
                    'state': intasend_state,
                    'details': {
                        'amount': result.get('amount'),
                        'currency': result.get('currency'),
                        'provider': result.get('provider'),
                        'mpesa_reference': result.get('mpesa_reference')
                    }
                })
        else:
            return Response({
                'error': f'Failed to check payment status: {result["error"]}',
                'payment_id': str(payment.id)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError as e:
        # Handle credential-related errors
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Status check failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([PublicKeyAuthentication])
@permission_classes([IsAuthenticated])
def create_intasend_payment_link(request):
    """Create IntaSend payment link for the given payment"""
    try:
        # Validate that we have a proper user (not AnonymousUser)
        if not request.user or request.user.is_anonymous:
            return Response({
                'error': 'Authentication required. Please provide a valid public API key in the X-Public-Key header.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get required data
        router_id = request.data.get('router_id')
        package_id = request.data.get('package_id')
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'mpesa')
        mac_address = request.data.get('mac_address', '')
        ip_address = request.data.get('ip_address', '')
        
        # Validate required fields
        if not all([router_id, package_id, phone_number, amount]):
            return Response({
                'error': 'router_id, package_id, phone_number, and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get router and package
        from routers.models import Router, Package
        try:
            router = Router.objects.get(pk=router_id, user=request.user)
        except Router.DoesNotExist:
            return Response({
                'error': 'Router not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            package = Package.objects.get(pk=package_id, router=router, is_active=True)
        except Package.DoesNotExist:
            return Response({
                'error': 'Package not found or not active for this router'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate amount matches package price
        if float(amount) != float(package.price):
            return Response({
                'error': f'Amount must match package price: {package.price} {package.currency}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            router=router,
            package=package,
            phone_number=phone_number,
            amount=amount,
            currency='KES',
            payment_method=payment_method,
            payment_provider='instasend',  # Set payment provider
            mac_address=mac_address,
            ip_address=ip_address,
            status='pending'
        )
        
        # Initialize IntaSend API with automatically fetched credentials
        intasend_api = IntaSendAPI(request.user)
        
        # Create payment link
        result = intasend_api.create_payment_link(payment)
        
        if result['success']:
            # Return payment details with IntaSend info
            response_serializer = PaymentSerializer(payment)
            return Response({
                'message': 'Payment link created successfully',
                'payment': response_serializer.data,
                'intasend': {
                    'payment_url': result['payment_url'],
                    'invoice_id': result['invoice_id'],
                    'state': result['state']
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # Mark payment as failed
            payment.status = 'failed'
            payment.error_message = result['error']
            payment.save()
            
            return Response({
                'error': f'Failed to create payment link: {result["error"]}',
                'message': 'Payment link creation failed',
                'payment_id': str(payment.id)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except ValueError as e:
        # Handle credential-related errors
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': f'Payment link creation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Mikrotik Login Page Views

def mikrotik_login_page(request):
    """Serve the Mikrotik login page"""
    try:
        # Read the HTML file and serve it
        with open('static/mikrotik-login.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholder values with actual configuration
        html_content = html_content.replace(
            'const PUBLIC_API_KEY = \'your_public_api_key_here\';',
            'const PUBLIC_API_KEY = \'c1eb9fed9dabc57f61d56c26ef3870ae\';'  # Replace with actual key
        )
        
        return HttpResponse(html_content, content_type='text/html')
        
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Login page not found</h1><p>Please ensure the login page HTML file exists.</p>',
            status=404
        )
    except Exception as e:
        return HttpResponse(
            f'<h1>Error loading login page</h1><p>{str(e)}</p>',
            status=500
        )

def mikrotik_login_enhanced(request):
    """Serve the enhanced Mikrotik login page"""
    try:
        # Read the enhanced HTML file and serve it
        with open('static/mikrotik-login-enhanced.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace placeholder values with actual configuration
        html_content = html_content.replace(
            'const PUBLIC_API_KEY = \'your_public_api_key_here\';',
            'const PUBLIC_API_KEY = \'c1eb9fed9dabc57f61d56c26ef3870ae\';'  # Replace with actual key
        )
        
        return HttpResponse(html_content, content_type='text/html')
        
    except FileNotFoundError:
        return HttpResponse(
            '<h1>Enhanced login page not found</h1><p>Please ensure the enhanced login page HTML file exists.</p>',
            status=404
        )
    except Exception as e:
        return HttpResponse(
            f'<h1>Error loading enhanced login page</h1><p>{str(e)}</p>',
            status=500
        )
