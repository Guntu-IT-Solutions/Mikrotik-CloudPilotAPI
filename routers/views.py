from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Router, Package
from .serializers import RouterSerializer, PackageSerializer
from .mikrotik_api import MikrotikAPIManager
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def router_list(request):
    """List all routers for the authenticated user or create a new one."""
    if request.method == 'GET':
        routers = Router.objects.filter(user=request.user)
        serializer = RouterSerializer(routers, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RouterSerializer(data=request.data)
        if serializer.is_valid():
            router = serializer.save(user=request.user)
            # Refresh serializer to get the created data with ID
            serializer = RouterSerializer(router)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def router_detail(request, pk):
    """Retrieve, update or delete a router."""
    try:
        router = Router.objects.get(pk=pk, user=request.user)
    except Router.DoesNotExist:
        return Response({
            'error': 'Router not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RouterSerializer(router)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RouterSerializer(router, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        router_name = router.name
        router.delete()
        return Response({
            'message': f'Router "{router_name}" has been successfully deleted'
        }, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_connection(request, pk):
    """Test connection to a specific router."""
    try:
        router = Router.objects.get(pk=pk, user=request.user)
    except Router.DoesNotExist:
        return Response({
            'error': 'Router not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        manager = MikrotikAPIManager()
        is_online = manager.test_connection(router)
        
        # Update router status
        router.is_online = is_online
        router.last_checked = timezone.now()
        router.save()
        
        return Response({
            'router_id': pk,
            'is_online': is_online,
            'message': 'Connection test completed'
        })
    except Exception as e:
        return Response({
            'error': f'Connection test failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def execute_command(request, pk):
    """Execute a custom command on a specific router."""
    try:
        router = Router.objects.get(pk=pk, user=request.user)
    except Router.DoesNotExist:
        return Response({
            'error': 'Router not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)
    
    command = request.data.get('command')
    if not command:
        return Response({
            'error': 'Command is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract optional parameters
    method = request.data.get('method', 'GET').upper()
    params = request.data.get('params', None)  # Query parameters for GET
    data = request.data.get('data', None)      # JSON data for POST/PUT
    
    # Validate method
    if method not in ['GET', 'POST', 'PUT', 'DELETE']:
        return Response({
            'error': 'Invalid HTTP method. Must be GET, POST, PUT, or DELETE'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        manager = MikrotikAPIManager()
        result = manager.execute_command(router, command, method, params, data)
        
        if result.get('success'):
            return Response({
                'router_id': pk,
                'command': command,
                'method': method,
                'result': result['data'],
                'message': 'Command executed successfully'
            })
        else:
            # Command failed on Mikrotik side
            return Response({
                'router_id': pk,
                'command': command,
                'method': method,
                'error': result['error'],
                'status_code': result.get('status_code', 400)
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'error': f'Command execution failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_device_info(request, pk):
    """Get device information from a specific router."""
    try:
        router = Router.objects.get(pk=pk, user=request.user)
    except Router.DoesNotExist:
        return Response({
            'error': 'Router not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        manager = MikrotikAPIManager()
        device_info = manager.get_device_info(router)
        
        return Response({
            'router_id': pk,
            'device_info': device_info,
            'message': 'Device information retrieved successfully'
        })
    except Exception as e:
        return Response({
            'error': f'Failed to get device info: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_router_packages(request, pk):
    """Get available packages for a specific router."""
    try:
        router = Router.objects.get(pk=pk, user=request.user)
    except Router.DoesNotExist:
        return Response({
            'error': 'Router not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    # Get active packages for this router
    packages = router.packages.filter(is_active=True)
    
    package_data = []
    for package in packages:
        package_data.append({
            'id': package.id,
            'name': package.name,
            'package_type': package.package_type,
            'package_type_display': package.get_package_type_display(),
            'duration_hours': package.duration_hours,
            'duration_display': package.duration_display,
            'price': str(package.price),
            'currency': 'KES',
            'download_speed_mbps': package.download_speed_mbps,
            'upload_speed_mbps': package.upload_speed_mbps,
            'download_speed_display': package.download_speed_display,
            'upload_speed_display': package.upload_speed_display,
            'speed_display': package.speed_display,
            'description': package.description,
            'is_active': package.is_active
        })
    
    return Response({
        'router_id': pk,
        'router_name': router.name,
        'packages': package_data,
        'message': f'Found {len(package_data)} active packages for {router.name}'
    })

@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def package_list(request):
    """List all packages for the authenticated user or create a new one."""
    if request.method == 'GET':
        # Get packages from routers owned by the user
        user_routers = Router.objects.filter(user=request.user)
        packages = Package.objects.filter(router__in=user_routers)
        serializer = PackageSerializer(packages, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PackageSerializer(data=request.data)
        if serializer.is_valid():
            # Verify the router belongs to the user
            router_id = serializer.validated_data.get('router').id
            try:
                router = Router.objects.get(pk=router_id, user=request.user)
            except Router.DoesNotExist:
                return Response({
                    'error': 'Router not found or access denied'
                }, status=status.HTTP_404_NOT_FOUND)
            
            package = serializer.save()
            # Refresh serializer to get the created data with ID
            serializer = PackageSerializer(package)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def package_detail(request, pk):
    """Retrieve, update or delete a package."""
    try:
        package = Package.objects.get(pk=pk)
        # Verify the package belongs to a router owned by the user
        if package.router.user != request.user:
            return Response({
                'error': 'Package not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
    except Package.DoesNotExist:
        return Response({
            'error': 'Package not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PackageSerializer(package)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PackageSerializer(package, data=request.data)
        if serializer.is_valid():
            # Verify the new router (if changed) belongs to the user
            new_router = serializer.validated_data.get('router')
            if new_router and new_router.user != request.user:
                return Response({
                    'error': 'Router not found or access denied'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        package_name = package.name
        package.delete()
        return Response({
            'message': f'Package "{package_name}" has been successfully deleted'
        }, status=status.HTTP_200_OK)
