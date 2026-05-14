from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    """Декоратор для проверки прав администратора"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_panel:login')
        if not request.user.is_staff and not request.user.is_superuser:
            return redirect('admin_panel:login')
        return view_func(request, *args, **kwargs)
    return wrapper