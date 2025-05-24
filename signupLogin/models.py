from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, default='Unknown')
    phone_number = models.CharField(max_length=20,default="")
    role = models.CharField(max_length=20, default='farmer')

    def __str__(self):
        return self.user.username

