from django.urls import path
from .views import *
urlpatterns = [
    path('',login,name="login"),
    path('register/ ',signup,name="signup"),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('administrator/',administrator,name="administrator"),
    path('farmer/',farmer,name="farmer"),
    path('home/',home,name="home"),
    path('profile/',profile,name="profile"),
    path('user/',user,name="user"),
    path('weather/',weather,name="weather"),

]
