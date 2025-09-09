from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .serializers import RegisterSerializer, APIKeySerializer
from .models import APIKey, UserProfile
from routers.authentication import validate_api_keys
from rest_framework_simplejwt.authentication import JWTAuthentication

@api_view(['POST'])
@csrf_exempt
def register(request):
    """Register a new user."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Create the user (this will trigger the signal to create API keys)
            user = serializer.save()
            
            # Get the API key that was created by the signal
            try:
                api_key = user.api_key
                api_key_data = {
                    "public_key": api_key.public_key,
                    "message": "Store your private key securely — it won't be shown again."
                }
            except:
                api_key_data = None
            
            return Response({
                "message": "User registered successfully",
                "user_id": user.id,
                "api_key": api_key_data,
                "note": "API keys created automatically"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                "error": f"Failed to create user: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@csrf_exempt
def login(request):
    """Login user and return JWT tokens."""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def api_key_login(request):
    """Login user using API keys and return JWT tokens."""
    public_key = request.data.get('public_key')
    private_key = request.data.get('private_key')
    
    if not public_key or not private_key:
        return Response({
            'error': 'Public key and private key are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate using API keys
    user = validate_api_keys(public_key, private_key)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id,
            'username': user.username,
            'message': 'API key authentication successful'
        })
    else:
        return Response({
            'error': 'Invalid API keys'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_api_key(request):
    """Generate a new API key for the authenticated user"""
    try:
        # Generate new API key
        public, private = APIKey.create_for_user(request.user)
        
        return Response({
            "message": "New API key generated successfully",
            "api_key": {
                "public_key": public,
                "private_key": private,
                "message": "Store your private key securely — it won't be shown again."
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "error": f"Failed to generate API key: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get or update user profile."""
    if request.method == 'GET':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        return Response({
            'bio': profile.bio,
            'website': profile.website,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at
        })
    
    elif request.method == 'PUT':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.bio = request.data.get('bio', profile.bio)
        profile.website = request.data.get('website', profile.website)
        profile.save()
        return Response({"message": "Profile updated successfully"})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_api_keys(request):
    """Get the user's API keys"""
    try:
        keys = request.user.api_key
        return Response(APIKeySerializer(keys).data)
    except:
        return Response({
            'error': 'No API keys found for this user'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def rotate_api_keys(request):
    """Generate new API keys for the user"""
    try:
        public, private = APIKey.create_for_user(request.user)
        return Response({
            "message": "New API keys generated. Store your private key securely — it won't be shown again.",
            "public_key": public,
            "private_key": private
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            "error": f"Failed to rotate API keys: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)