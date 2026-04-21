from django.shortcuts import redirect
from django.contrib import messages

def client_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login to access this page.')
            return redirect('admin:login')
        return view_func(request, *args, **kwargs)
    return wrapper