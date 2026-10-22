from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator for views that require administrator privileges.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the Administrator Dashboard.")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        if not request.user.is_admin_user:
            messages.error(request, "Access denied. Administrator privileges are required.")
            return redirect('accounts:student_dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def student_required(view_func):
    """
    Decorator for views that require student account login.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to continue.")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        
        if request.user.is_admin_user:
            return redirect('dashboard:admin_dashboard')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def approved_voter_required(view_func):
    """
    Decorator for voting actions that strictly require approved student status.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in with your verified student account to vote.")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        if request.user.is_admin_user:
            messages.warning(request, "Administrators cannot cast student ballots.")
            return redirect('dashboard:admin_dashboard')

        if not request.user.is_approved_voter:
            if request.user.approval_status == 'pending':
                messages.warning(request, "Your registration is pending administrator approval. You cannot cast a vote until approved.")
            elif request.user.approval_status == 'rejected':
                messages.error(request, "Your student account registration was rejected. Voting is disabled.")
            else:
                messages.error(request, "Your student account is deactivated or unauthorized for voting.")
            return redirect('accounts:student_dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view
