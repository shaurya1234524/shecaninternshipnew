from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
from django.db import models
from django.conf import settings


from django.utils import timezone
import random

# Custom User Model (optional)
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# models.py

class OTPModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=[('signup', 'Signup'), ('reset', 'Reset Password')])
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))
