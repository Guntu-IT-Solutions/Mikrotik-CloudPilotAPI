# core/middleware.py
import threading
from django.utils.deprecation import MiddlewareMixin


# Thread-local storage for current user
_thread_locals = threading.local()


def get_current_user():
    """Get the current user from thread local storage."""
    return getattr(_thread_locals, 'current_user', None)


def set_current_user(user):
    """Set the current user in thread local storage."""
    _thread_locals.current_user = user


class UserContextMiddleware(MiddlewareMixin):
    """
    Middleware to store the current user in thread local storage
    so the database router can access user context.
    """
    
    def process_request(self, request):
        """Store the authenticated user in thread local storage."""
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
    
    def process_response(self, request, response):
        """Clean up thread local storage."""
        set_current_user(None)
        return response
    
    def process_exception(self, request, exception):
        """Clean up thread local storage on exceptions."""
        set_current_user(None)
        return None
