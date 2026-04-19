"""
accounts/views.py
-----------------
Login, logout, and admin-only user management views.
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden

from .forms import LoginForm, CreateUserForm
from .models import User


def login_view(request):
    """
    Show login page and authenticate the user.
    After login, redirect to /dashboard/.
    """
    # If already logged in, go straight to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Support ?next= redirect (Django's standard)
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Log the user out and redirect to login page."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def manage_users(request):
    """
    Admin-only: list all users and create new ones.
    """
    if not request.user.is_admin_role:
        return HttpResponseForbidden("Only admins can manage users.")

    users = User.objects.all().order_by('role', 'username')
    form = CreateUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"User '{form.cleaned_data['username']}' created successfully.")
            return redirect('manage_users')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'accounts/manage_users.html', {
        'users': users,
        'form': form,
    })


@login_required
def delete_user(request, pk):
    """Admin-only: delete a user (cannot delete yourself)."""
    if not request.user.is_admin_role:
        return HttpResponseForbidden("Only admins can delete users.")

    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('manage_users')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f"User '{username}' deleted.")
        return redirect('manage_users')

    return render(request, 'accounts/confirm_delete_user.html', {'target_user': user})
