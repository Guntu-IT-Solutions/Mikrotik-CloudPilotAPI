from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings
import os

def serve_docs(request, path=''):
    """
    Serve MkDocs documentation from the static files directory.
    This allows the documentation to be served through Django.
    """
    # Build the full path to the documentation file
    if not path:
        path = 'index.html'
    
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
        # Try to serve index.html for 404s (SPA routing)
        index_path = os.path.join(settings.STATIC_ROOT, 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                return HttpResponse(f.read(), content_type='text/html')
        
        # If still not found, try STATICFILES_DIRS
        for static_dir in settings.STATICFILES_DIRS:
            index_path = os.path.join(static_dir, 'index.html')
            if os.path.exists(index_path):
                with open(index_path, 'rb') as f:
                    return HttpResponse(f.read(), content_type='text/html')
        
        # Provide detailed error information for debugging
        error_msg = f"""
        Documentation not found: {path}
        
        Searched in:
        - STATIC_ROOT: {settings.STATIC_ROOT}
        - STATICFILES_DIRS: {settings.STATICFILES_DIRS}
        
        Available files in STATIC_ROOT:
        {os.listdir(settings.STATIC_ROOT) if os.path.exists(settings.STATIC_ROOT) else 'Directory not found'}
        """
        return HttpResponse(error_msg, status=404)
    
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
