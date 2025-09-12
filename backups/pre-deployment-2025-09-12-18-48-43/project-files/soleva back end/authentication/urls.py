from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # JWT token endpoints
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password management
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/change/', views.ChangePasswordView.as_view(), name='password_change'),
    
    # Email verification
    path('verify/email/', views.EmailVerificationView.as_view(), name='email_verification'),
    path('verify/resend/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # Social authentication
    path('social/', views.SocialAuthView.as_view(), name='social_auth'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]
