from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.utils import timezone
from django.db import connection
from django.core.cache import cache
import os
import psutil
import platform

def serve_docs(request, path=''):
    """
    Serve MkDocs documentation from the static files directory.
    This allows the documentation to be served through Django.
    """
    # Check if this is an API endpoint - if so, let Django handle it
    api_prefixes = ['users/', 'routers/', 'payments/', 'admin/']
    if any(path.startswith(prefix) for prefix in api_prefixes):
        # This is an API endpoint, let Django handle the routing
        # Return a 404 so Django can process it properly
        from django.http import Http404
        raise Http404(f"API endpoint '{path}' not found")
    
    
    # Ensure the path is safe (no directory traversal)
    if '..' in path or path.startswith('/'):
        return HttpResponse('Invalid path', status=400)
    
    # Build the full file path - try both STATIC_ROOT and STATICFILES_DIRS
    docs_path = os.path.join(settings.STATIC_ROOT, path)
    
    # If not found in STATIC_ROOT, try STATICFILES_DIRS
    if not os.path.exists(docs_path):
        for static_dir in settings.STATICFILES_DIRS:
            test_path = os.path.join(static_dir, path)
            if os.path.exists(test_path):
                docs_path = test_path
                break
    
    # Check if the path exists and handle directories
    if os.path.exists(docs_path):
        if os.path.isdir(docs_path):
            # If it's a directory, try to serve index.html from it
            index_path = os.path.join(docs_path, 'index.html')
            if os.path.exists(index_path):
                docs_path = index_path
            else:
                # If no index.html, try to list directory contents or redirect
                return HttpResponse(f'Directory listing not available. Try: {path}/index.html', status=404)
        # Continue with the file (either original or index.html from directory)
    else:
        # Serve index.html for 404s (SPA routing)
        index_path = os.path.join(docs_path, 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='text/html')
        
        # This is a genuine 404 - let Django handle it
        from django.http import Http404
        raise Http404(f"Documentation page '{path}' not found")
    
    # Determine content type based on file extension
    content_type = 'text/plain'
    if path.endswith('.html'):
        content_type = 'text/html'
    elif path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'application/javascript'
    elif path.endswith('.png'):
        content_type = 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif path.endswith('.svg'):
        content_type = 'image/svg+xml'
    elif path.endswith('.ico'):
        content_type = 'image/x-icon'
    
    # Serve the file
    try:
        with open(docs_path, 'rb') as f:
            return HttpResponse(f.read(), content_type=content_type)
    except Exception as e:
        return HttpResponse(f'Error reading file: {str(e)}', status=500)

def docs_home(request):
    """
    Serve the main documentation page.
    """
    return serve_docs(request, 'index.html')

def health_check(request):
    """
    Health check endpoint for monitoring server status.
    Returns server health information including database connectivity,
    system resources, and application status.
    """
    try:
        # Check database connectivity
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check cache connectivity
    try:
        cache.set('health_check_test', 'ok', 10)
        cache_status = "healthy" if cache.get('health_check_test') == 'ok' else "error"
    except Exception as e:
        cache_status = f"error: {str(e)}"
    
    # Get system information
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_info = {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "platform": platform.system(),
            "python_version": platform.python_version(),
        }
    except Exception as e:
        system_info = {"error": str(e)}
    
    # Get application information
    import django
    app_info = {
        "django_version": django.get_version(),
        "debug_mode": settings.DEBUG,
        "timezone": str(timezone.now().tzinfo),
        "current_time": timezone.now().isoformat(),
        "allowed_hosts": settings.ALLOWED_HOSTS,
    }
    
    # Determine overall health status
    overall_status = "healthy"
    if db_status != "healthy" or cache_status != "healthy":
        overall_status = "degraded"
    
    if "error" in str(system_info):
        overall_status = "degraded"
    
    # Prepare response
    health_data = {
        "status": overall_status,
        "timestamp": timezone.now().isoformat(),
        "database": db_status,
        "cache": cache_status,
        "system": system_info,
        "application": app_info,
    }
    
    # Return appropriate HTTP status code
    if overall_status == "healthy":
        status_code = 200
    elif overall_status == "degraded":
        status_code = 200  # Still operational but with issues
    else:
        status_code = 503  # Service unavailable
    
    # Check if client wants JSON response
    if request.META.get('HTTP_ACCEPT', '').find('application/json') != -1:
        import json
        return HttpResponse(
            json.dumps(health_data, indent=2),
            content_type='application/json',
            status=status_code
        )
    else:
        # Return plain text response for simple monitoring
        return HttpResponse(
            f"Health Check: {overall_status.upper()}\n\n" +
            f"Database: {db_status}\n" +
            f"Cache: {cache_status}\n" +
            f"CPU: {system_info.get('cpu_percent', 'N/A')}%\n" +
            f"Memory: {system_info.get('memory_percent', 'N/A')}%\n" +
            f"Disk: {system_info.get('disk_percent', 'N/A')}%\n" +
            f"Time: {app_info['current_time']}\n",
            content_type='text/plain',
            status=status_code
        )
