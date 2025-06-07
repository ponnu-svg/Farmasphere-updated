import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
import requests
from django.http import JsonResponse
from .models import Contact, Profile ,User 
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import ContactForm

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Login attempt - Username: {username}, Password: {password}")

        try:
            user_obj = User.objects.get(username=username)
            print(f"User found: {user_obj}, is_active: {user_obj.is_active}")

            if user_obj.password == password:
                auth_login(request, user_obj)
                try:
                    profile = Profile.objects.get(user=user_obj)
                    print(f"Profile found: {profile}")
                except Profile.DoesNotExist:
                    messages.error(request, "User profile not found")
                    return redirect('login')

                # request.session['user_id'] = user_obj.id  # Simulate login
                # request.session['username'] = user_obj.username
                print(profile.role)
                if profile.role == 'farmer':
                    return redirect('farmer')
                elif profile.role == 'merchant':
                    return redirect('merchant')
                else:
                    messages.error(request, 'Invalid role assigned to your account.')
                    return redirect('login')
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('login')

        except User.DoesNotExist:
            print("User does not exist")
            messages.error(request, 'User does not exist')
            return redirect('login')

    return render(request, 'signupLogin/login.html')



def signup(request):
    if request.method == 'POST':
        # Get form data
        request.session['signup_username'] = request.POST.get('username')
        request.session['signup_email'] = request.POST.get('email')
        request.session['signup_full_name'] = request.POST.get('full_name')
        request.session['signup_phone_number'] = request.POST.get('phone_number')
        request.session['signup_role'] = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Basic validations
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if User.objects.filter(username=request.session['signup_username']).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        # Save password securely in session (not recommended for production — use temp table or cache)
        request.session['signup_password'] = password

        # Generate and send OTP
        otp = random.randint(100000, 999999)
        request.session['signup_otp'] = otp

        send_mail(
            'Your OTP for Account Signup',
            f'Your OTP is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [request.session['signup_email']],
            fail_silently=False,
        )

        messages.success(request, 'OTP sent to your email.')
        return redirect('signup_verify_otp')

    return render(request, 'signupLogin/signup.html', {'MEDIA_URL': settings.MEDIA_URL})


# def signup_otp(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
    
#         signup_otp = random.randint(100000, 999999)
#         request.session['signup_email'] = email
#         request.session['signup_otp'] = signup_otp

#         # Send OTP via email
#         send_mail(
#             'Your OTP for Password Reset',
#             f'Your OTP is {signup_otp}',
#             settings.DEFAULT_FROM_EMAIL,
#             [email],
#             fail_silently=False,
#         )

#         messages.success(request, 'OTP sent to your email.')
#         return redirect('signup_verify_otp')

       

#     return render(request, 'signupLogin/.html')

def signup_verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('signup_otp')

        if not entered_otp or not session_otp:
            messages.error(request, 'OTP session expired or missing.')
            return redirect('signup')

        if int(entered_otp) != int(session_otp):
            messages.error(request, 'Invalid OTP.')
            return redirect('signup_verify_otp')

        # OTP verified — create user now
        username = request.session.get('signup_username')
        email = request.session.get('signup_email')
        full_name = request.session.get('signup_full_name')
        phone_number = request.session.get('signup_phone_number')
        password = request.session.get('signup_password')
        role = request.session.get('signup_role')

        print("username:",username)
        print("email:",email)
        print("full_name:",full_name)
        print("phone_number:",phone_number)
        print("password:",password)
        print("role:",role)


        user = User.objects.create(username=username, email=email, password=password)
        print(user)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.full_name = full_name
        profile.phone_number = phone_number
        profile.role = role
        profile.save()

        # Clear session data
        for key in ['signup_username', 'signup_email', 'signup_full_name', 'signup_phone_number', 'signup_password', 'signup_otp']:
            request.session.pop(key, None)

        messages.success(request, 'OTP verified. Account created successfully!')
        return redirect('login')

    return render(request, 'signupLogin/signup_otp.html')



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
        session_otp = request.session.get('otp')

        if not entered_otp or not session_otp:
            messages.error(request, 'OTP session expired or missing.')
            return redirect('verify_otp')

        try:
            if int(entered_otp) == int(session_otp):
                messages.success(request, 'OTP verified. You may now reset your password.')
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP.')
        except ValueError:
            messages.error(request, 'OTP must be a valid number.')

        return redirect('verify_otp')

    return render(request, 'signupLogin/verify_otp.html')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password')

        email = request.session.get('reset_email')
        if not email:
            messages.error(request, 'Session expired. Please restart the process.')
            return redirect('login')

        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful! Please login.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('reset_password')

    return render(request, 'signupLogin/reset_password.html')


def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Contact.objects.filter(email=email).exists():
                messages.error(request, 'You have already submitted a response with this email.')
            else:
                form.save()
                messages.success(request, 'Your response has been received!')
                return redirect('home') 
    else:
        form = ContactForm()

    return render(request, 'home.html', {'form': form})

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
    # try:
    #     role = request.user.profile.role.lower()
    #     print(f"Farmer view - User: {request.user.username}, Role: {role}")
    #     if role != 'farmer':
    #         messages.error(request, 'Unauthorized access')
    #         return redirect('login')
    # except Profile.DoesNotExist:
    #     messages.error(request, 'Profile not found')
    #     return redirect('login')

    return render(request, 'dashboard/farmer-dashboard.html')


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

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your response has been received!.')

    else:
        form = ContactForm()
    return render(request, 'home.html', {'form': form})
