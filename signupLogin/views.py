import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
import requests
from django.http import JsonResponse
from .models import Profile  
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Login attempt - Username: {username}, Password: {password}")

        try:
            user_obj = User.objects.get(username=username)
            print(f"User found: {user_obj}, is_active: {user_obj.is_active}")
            print(f"Password correct: {user_obj.check_password(password)}")
        except User.DoesNotExist:
            print("User does not exist")

        user = authenticate(request, username=username, password=password)
        print(f"Authenticated user: {user}")

        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
                print(f"Profile found: {profile}")
            except Profile.DoesNotExist:
                messages.error(request, "User profile not found")
                return redirect('login')

            auth_login(request, user)

            # Redirect based on stored role
            if profile.role == 'farmer':
                return redirect('farmer')  # Make sure 'farmer' is a valid URL name
            elif profile.role == 'admin':
                return redirect('administrator')
            else:
                messages.error(request, 'Invalid role assigned to your account.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'signupLogin/login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        # Password match check
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')  # or 'signup' based on your urls.py

        # Username exists check
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)

        # Profile must be linked here — ensure Profile is auto-created (via signal) or create if not
        profile, created = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        print("Redirecting to login...")
        messages.success(request, 'Account created successfully!')
        return redirect('login')

    return render(request, 'signupLogin/signup.html', {'MEDIA_URL': settings.MEDIA_URL})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = random.randint(100000, 999999)
            request.session['reset_email'] = email
            request.session['otp'] = otp

            # Send OTP via email
            send_mail(
                'Your OTP for Password Reset',
                f'Your OTP is {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, 'OTP sent to your email.')
            return redirect('verify_otp')

        except User.DoesNotExist:
            messages.error(request, 'No user with this email.')
            return redirect('forgot_password')

    return render(request, 'signupLogin/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if int(entered_otp) == int(request.session.get('otp')):
            messages.success(request, 'OTP verified. You may reset your password.')
            return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP.')
            return redirect('verify_otp')
    return render(request, 'signupLogin/verify_otp.html')

def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')

        email = request.session.get('reset_email')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        messages.success(request, 'Password reset successful! Please login.')
        return redirect('login')

    return render(request, 'signupLogin/reset_password.html')


def home(request):
    return render(request,'home.html')

def profile(request):
    return render(request,'profile.html')

@login_required
def administrator(request):
    try:
        role = request.user.profile.role.lower()
        print(f"Administrator view - User: {request.user.username}, Role: {role}")
        if role != 'admin':
            messages.error(request, 'Unauthorized access')
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('login')

    return render(request, 'dashboard/admin-dashboard.html')

@login_required
def farmer(request):
    try:
        role = request.user.profile.role.lower()
        print(f"Farmer view - User: {request.user.username}, Role: {role}")
        if role != 'farmer':
            messages.error(request, 'Unauthorized access')
            return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, 'Profile not found')
        return redirect('login')

    return render(request, 'dashboard/farmer-dashboard.html', {'profile': request.user.profile})


def user(request):
    return render(request,'user-management.html')

# def weathertest(request):
#     return render(request,'weathertest1.html')
def weather(request):
    return render(request, 'weathertest.html')

def fetch_weather_data(city):
    api_key = 'Yd4693228a24cbd258bd1bb096e4514e2'  # Replace with your API key
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    return response.json()

# View to render the weather page
# def weather_view(request):
#     return render(request, 'weather.html')

# API endpoint to fetch weather for a specific area
# def weather_api(request, area):
#     # Fetch weather for the given area
#     weather_data = fetch_weather_data(area)
    
#     # Structure the data to send back as JSON
#     data = {
#         'city': weather_data.get('name'),
#         'temperature': weather_data['main']['temp'],
#         'humidity': weather_data['main']['humidity'],
#         'conditions': weather_data['weather'][0]['description'],
#     }
    
#     return JsonResponse(data)
