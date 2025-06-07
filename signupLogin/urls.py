from django.urls import path,include
from .views import *


urlpatterns = [
    path('login/',login,name="login"),
    path('register/ ',signup,name="signup"),
    # path('signup_otp/ ',signup_otp,name="signup_otp"),
    path('signup_verify_otp/', signup_verify_otp, name='signup_verify_otp'),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('administrator/',administrator,name="administrator"),
    path('farmer/',farmer,name="farmer"),
    path('',home,name="home"),
    path('profile/',profile,name="profile"),
    path('user/',user,name="user"),
    path('weather/',weather,name="weather"),
]
