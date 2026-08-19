from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from listings.models import Bookmark


def register(request):
    print("=== register view called ===")
    print("Method:", request.method)
    if request.method == 'POST':
        print("POST data:", request.POST)
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not first_name or not last_name or not email or not password or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/register.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        login(request, user)
        messages.success(request, f"Welcome {first_name}! Registration successful.")
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'accounts/login.html')
    else:
        return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('wallpaper')
    context = {
        'user': request.user,
        'bookmarks': bookmarks,
    }
    return render(request, 'accounts/dashboard.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('accounts:login')