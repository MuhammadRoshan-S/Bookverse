from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-create a profile
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to Bookverse, {user.username}!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Auto-create profile if missing
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    """Profile settings page — change avatar / bio."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update avatar if uploaded
        if 'avatar' in request.FILES:
            if profile.avatar:
                profile.avatar.delete(save=False)
            profile.avatar = request.FILES['avatar']
        # Update bio
        profile.bio = request.POST.get('bio', '')
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'profile': profile})
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.models import User

def seller_register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('seller_register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return redirect('seller_register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('seller_register')

        user = User.objects.create_user(username=username, email=email, password=password)
        # Create profile with seller role
        UserProfile.objects.create(user=user, role='seller')
        
        login(request, user)
        messages.success(request, 'Seller account created successfully. Welcome to your dashboard!')
        return redirect('dashboard:seller_home') # we will namespace dashboard

    return render(request, 'accounts/seller_register.html')
