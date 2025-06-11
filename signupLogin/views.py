import random
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
import requests
from django.http import HttpResponseForbidden, JsonResponse
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import *
from .utils import haversine_distance

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
                    profile = User.objects.get(username=user_obj.username)
                    print(f"Profile found: {profile}")
                except Profile.DoesNotExist:
                    messages.error(request, "User profile not found")
                    return redirect('login')

                # request.session['user_id'] = user_obj.id  # Simulate login
                # request.session['username'] = user_obj.username
                print(profile.role)
                if profile.role == 'farmer':
                    return redirect('farmer_page')
                elif profile.role == 'merchant':
                    return redirect('merchant_page')
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

def logout(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

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


# def user(request):
#     return render(request,'user-management.html')

# def weathertest(request):
#     return render(request,'weathertest1.html')
def weather(request):
    return render(request, 'weathertest.html')

def fetch_weather_data(city):
    api_key = 'Yd4693228a24cbd258bd1bb096e4514e2'  # Replace with your API key
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    return response.json()

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your response has been received!.')

    else:
        form = ContactForm()
    return render(request, 'home.html', {'form': form})

#  merchants's Views
def merchant_page(request):
    if not request.user.is_authenticated or request.user.role != 'merchant':
        messages.error(request, "You don’t have access to that page. So you have been redirected.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method == "POST":
        form = MerchantRequestForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, "Demand posted successfully!")
            return redirect('merchant_page')
    else:
        form = MerchantRequestForm()

    # Get the latest merchant request from this user (optional: get location from there)
    latest_request = MerchantRequest.objects.filter(user=request.user).order_by('-created_at').first()

    farmer_products = FarmerProduct.objects.all()

    # If merchant location is available, filter nearby
    if latest_request and latest_request.latitude and latest_request.longitude:
        nearby_products = []
        for fp in farmer_products:
            if fp.latitude and fp.longitude:
                distance = haversine_distance(
                    latest_request.latitude,
                    latest_request.longitude,
                    fp.latitude,
                    fp.longitude
                )
                if distance <= 50:  # Within 50 km
                    nearby_products.append(fp)
        farmer_products = nearby_products

    return render(request, 'merchants.html', {
        'form': form,
        'farmer_products': farmer_products
    })

@login_required
def merchant_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'merchant':
        messages.error(request, "You don’t have access to that page.So you have redirected to home page")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        merchant_requests = MerchantRequest.objects.filter(user=request.user)
        return render(request, 'merchant_dashboard.html', {'merchant_requests': merchant_requests})


@login_required
def farmer_page(request):
    if not request.user.is_authenticated or request.user.role != 'farmer':
        messages.error(request, "You don’t have access to that page. So you have been redirected.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == "POST":
        form = FarmerProductForm(request.POST)
        if form.is_valid():
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (TypeError, ValueError):
                messages.error(request, "Location not available. Please allow location access.")
                return redirect('farmer_page')

            product = form.save(commit=False)
            product.user = request.user
            product.latitude = latitude
            product.longitude = longitude
            product.save()

            messages.success(request, "Product posted successfully!")
            return redirect('farmer_page')
    else:
        form = FarmerProductForm()

    # Get the latest product posted by the farmer (used to determine location)
    latest_product = FarmerProduct.objects.filter(user=request.user).order_by('-posted_at').first()
    merchant_requests = MerchantRequest.objects.all()

    # Filter merchant requests based on proximity
    if latest_product and latest_product.latitude and latest_product.longitude:
        nearby_requests = []
        for req in merchant_requests:
            if req.latitude and req.longitude:
                distance = haversine_distance(
                    latest_product.latitude,
                    latest_product.longitude,
                    req.latitude,
                    req.longitude
                )
                if distance <= 50:  # within 50 km
                    nearby_requests.append(req)
        merchant_requests = nearby_requests

    return render(request, 'farmers.html', {
        'form': form,
        'merchant_requests': merchant_requests
    })

@login_required
def farmer_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'farmer':
        messages.error(request, "You don’t have access to that page.So you have redirected to home page")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        farmer_requests = FarmerProduct.objects.filter(user=request.user)
        return render(request, 'farmer_dashboard.html', {'farmer_requests': farmer_requests})

@login_required
def create_request(request):
    if request.user.role not in ['merchant', 'farmer']:
        messages.error(request, "You don’t have access to that page.So you have redirected to home page")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.user.role == 'farmer':
        form = FarmerProductForm(request.POST or None)
    else:
        form = MerchantRequestForm(request.POST or None)
    if form.is_valid():
        merchant_req = form.save(commit=False)
        merchant_req.user = request.user
        merchant_req.save()
        if request.user.role=='farmer':
            return redirect('farmer_dashboard')
        else:
            return redirect('merchant_dashboard')

    return render(request, 'create_request.html', {'form': form})

@login_required
def update_request(request, pk):
    if request.user.role not in ['merchant', 'farmer']:
        messages.error(request, "You don’t have access to that page.So you have redirected to home page")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.user.role == 'farmer':
        request_obj = get_object_or_404(FarmerProduct, pk=pk, user=request.user)
        form = FarmerProductForm(request.POST or None, instance=request_obj)
    else:
        request_obj = get_object_or_404(MerchantRequest, pk=pk, user=request.user)
        form = MerchantRequestForm(request.POST or None, instance=request_obj)
    if form.is_valid():
        form.save()
        if request.user.role=='farmer':
            return redirect('farmer_dashboard')
        else:
            return redirect('merchant_dashboard')
    return render(request, 'update_request.html', {'form': form})

@login_required
def delete_request(request, pk):
    if request.user.role != 'merchant' | request.user.role != 'farmer':
        messages.error(request, "You don’t have access to that page.So you have redirected to home page")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if request.user.role == 'farmer':
        request_obj = get_object_or_404(FarmerProduct, pk=pk, user=request.user)
    else:
        request_obj = get_object_or_404(MerchantRequest, pk=pk, user=request.user)
    if request.method == 'POST':
        request_obj.delete()
        if request.user.role=='farmer':
            return redirect('farmer_dashboard')
        else:
            return redirect('merchant_dashboard')
    return render(request, 'delete_confirm.html', {'request_obj': request_obj})






