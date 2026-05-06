from django.shortcuts import redirect
from functools import wraps

def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def role_required_custom(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'user_role' not in request.session:
                return redirect('login')
            if request.session['user_role'] not in allowed_roles:
                # Redirect to their own dashboard or home if unauthorized
                role = request.session.get('user_role')
                if role == 'volunteer':
                    return redirect('volunteer_dashboard')
                elif role == 'nssleader':
                    return redirect('leader_dashboard')
                elif role == 'admin':
                    return redirect('admin_dashboard')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
