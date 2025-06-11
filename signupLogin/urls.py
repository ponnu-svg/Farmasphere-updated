from django.urls import path,include
from .views import *


urlpatterns = [
    path('login/',login,name="login"),
    path('logout/',logout,name='logout'),
    path('register/ ',signup,name="signup"),
    # path('signup_otp/ ',signup_otp,name="signup_otp"),
    path('signup_verify_otp/', signup_verify_otp, name='signup_verify_otp'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    # path('administrator/',administrator,name="administrator"),
    path('',home,name="home"),
    # path('profile/',profile,name="profile"),
    # path('user/',user,name="user"),
    path('weather/',weather,name="weather"),
    path('merchants/', merchant_page, name='merchant_page'),
    path('farmers/', farmer_page, name='farmer_page'),
    path('merchant/dashboard/', merchant_dashboard, name='merchant_dashboard'),
    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('merchant/create/', create_request, name='create_request'),
    path('merchant/edit/<int:pk>/', update_request, name='update_request'),
    path('merchant/delete/<int:pk>/', delete_request, name='delete_request'),
    path('farmer/create/', create_request, name='farmer_create_request'),
    path('farmer/edit/<int:pk>/', update_request, name='farmer_update_request'),
    path('farmer/delete/<int:pk>/', delete_request, name='farmer_delete_request'),
    
]
