from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import authenticate, login
from .forms import SignupForm, LoginForm, ForgotPasswordForm, OTPVerifyForm
from .models import OTPModel
from django.contrib import messages


from django.core.mail import send_mail
from django.conf import settings  # <--- this is needed
from .models import OTPModel     # adjust import as needed

def send_otp(user, purpose):
    # Invalidate previous unused OTPs for the same purpose
    OTPModel.objects.filter(user=user, purpose=purpose, is_used=False).delete()

    otp = OTPModel.objects.create(
        user=user,
        code=OTPModel.generate_otp(),
        purpose=purpose
    )

    subject = f"Your OTP for {purpose.capitalize()}"
    message = f"Hello {user.username},\n\nYour OTP is: {otp.code}\n\nIt is valid for 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)

    return otp


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False  # Disable until OTP verified
            user.save()
            send_otp(user, 'signup')
            request.session['otp_user'] = user.id
            return redirect('verify_otp')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request, username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Account not verified.')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('otp_user')
    if not user_id:
        return redirect('signup')

    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            otp = OTPModel.objects.filter(user=user, code=otp_code, is_used=False, purpose='signup').first()
            if otp and not otp.is_expired():
                user.is_active = True
                user.save()
                otp.is_used = True
                otp.save()
                messages.success(request, "Account verified. Please login.")
                return redirect('login')
            else:
                messages.error(request, "Invalid or expired OTP.")
    else:
        form = OTPVerifyForm()
    return render(request, 'verify_otp.html', {'form': form})


def resend_otp_view(request):
    user_id = request.session.get('otp_user')
    if not user_id:
        return redirect('signup')
    user = User.objects.get(id=user_id)
    send_otp(user, 'signup')
    messages.success(request, 'OTP resent.')
    return redirect('verify_otp')


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                send_otp(user, 'reset')
                request.session['reset_user'] = user.id
                return redirect('reset_otp_verify')
            else:
                messages.error(request, 'Email not found.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})


def reset_otp_verify_view(request):
    user_id = request.session.get('reset_user')
    if not user_id:
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp']
            otp = OTPModel.objects.filter(user=user, code=otp_code, purpose='reset', is_used=False).first()
            if otp and not otp.is_expired():
                otp.is_used = True
                otp.save()
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP.')
    else:
        form = OTPVerifyForm()
    return render(request, 'reset_otp_verify.html', {'form': form})


def reset_password_view(request):
    user_id = request.session.get('reset_user')
    if not user_id:
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)
    if request.method == 'POST':
        password = request.POST.get('password')
        user.set_password(password)
        user.save()
        messages.success(request, 'Password reset. Please login.')
        return redirect('login')
    return render(request, 'reset_password.html')
from django.shortcuts import render
from django.http import JsonResponse

def login_page(request):
    return render(request, "dashboard/login.html")

def signup_page(request):
    return render(request, "dashboard/signup.html")

def dashboard(request):
    data = {
        "name": "Shaurya Singh",
        "referral_code": "shaurya2025",
        "donations": 4200,
        "rewards": ["Bronze ", "Silver", "Gold","Platinum"]
    }
    return render(request, "dashboard.html", {"data": data})

def leaderboard(request):
    leaders = [
        {"name": "Ananya", "donations": 9000},
        {"name": "Shaurya", "donations": 4200},
        {"name": "Ravi", "donations": 3200}
    ]
    return render(request, "leaderboard.html", {"leaders": leaders})

# Optional API Endpoint
def api_data(request):
    return JsonResponse({
        "name": "Shaurya Singh",
        "referral_code": "shaurya2025",
        "donations": 4200
    })
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # or redirect('/') to go home
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def user_dummy_api(request):
    dummy_data = {
        "name": "Shaurya Singh",
        "referral_code": "shaurya2025",
        "total_donations": 4200,
        "rewards": [
            {"title": "Bronze Badge", "unlocked": True},
            {"title": "Silver Badge", "unlocked": True},
            {"title": "Gold Badge", "unlocked": False},
            {"title": "Platinum Badge", "unlocked": False}
        ]
    }
    return Response(dummy_data)
