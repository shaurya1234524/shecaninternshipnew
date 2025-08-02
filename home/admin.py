from django.contrib import admin
from .models import CustomUser, OTPModel

admin.site.register(CustomUser)
admin.site.register(OTPModel)
