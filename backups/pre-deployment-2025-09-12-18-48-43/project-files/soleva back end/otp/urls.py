from django.urls import path
from .views import (
    GenerateOTPView, VerifyOTPView, ResendOTPView, OTPStatusView,
    CompleteRegistrationView, CompletePasswordResetView
)

app_name = 'otp'

urlpatterns = [
    # OTP Generation and Verification
    path('generate/', GenerateOTPView.as_view(), name='generate_otp'),
    path('verify/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend/', ResendOTPView.as_view(), name='resend_otp'),
    path('status/', OTPStatusView.as_view(), name='otp_status'),
    
    # Complete flows
    path('complete-registration/', CompleteRegistrationView.as_view(), name='complete_registration'),
    path('complete-password-reset/', CompletePasswordResetView.as_view(), name='complete_password_reset'),
]
