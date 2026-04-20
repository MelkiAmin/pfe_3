from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', views.RefreshTokenView.as_view(), name='token-refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('2fa/setup/', views.TwoFactorSetupView.as_view(), name='two-factor-setup'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='two-factor-verify'),
    path('2fa/disable/', views.TwoFactorDisableView.as_view(), name='two-factor-disable'),
    # Password reset
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # Organizer approval
    path('organizers/pending/', views.ListPendingOrganizersView.as_view(), name='list-pending-organizers'),
    path('organizers/<int:user_id>/approve/', views.ApproveOrganizerView.as_view(), name='approve-organizer'),
    path('organizers/<int:user_id>/reject/', views.RejectOrganizerView.as_view(), name='reject-organizer'),
]
