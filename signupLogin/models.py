from django.db import models
from django.contrib.auth.models import AbstractUser

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class User(AbstractUser):
    full_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=20, default='farmer')

    def __str__(self):
        return f"{self.full_name} ({self.username})"

class Profile(models.Model):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('merchant', 'Merchant'),
    )
    user = models.OneToOneField('signupLogin.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=15, default="")

    def __str__(self):
        return f"{self.user.username} - {self.role}"
