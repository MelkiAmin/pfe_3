import secrets

from django.core.cache import cache
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
import pyotp

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    LoginSerializer,
    RefreshTokenSerializer,
    LogoutSerializer,
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    TwoFactorDisableSerializer,
    EmailVerifySerializer,
)

# ─── Inline response schemas ──────────────────────────────────────────────────

_token_pair = inline_serializer('TokenPair', fields={
    'refresh': serializers.CharField(),
    'access':  serializers.CharField(),
})

_auth_response = inline_serializer('AuthResponse', fields={
    'user':   UserProfileSerializer(),
    'tokens': _token_pair,
})

_msg = inline_serializer('MessageResponse', fields={'detail': serializers.CharField()})

_refresh_response = inline_serializer('RefreshTokenResponse', fields={
    'access':  serializers.CharField(),
    'refresh': serializers.CharField(required=False),
})

_2fa_setup_response = inline_serializer('TwoFactorSetupResponse', fields={
    'secret':         serializers.CharField(),
    'otp_auth_url':   serializers.CharField(),
    'manual_entry_key': serializers.CharField(),
})

_2fa_status_response = inline_serializer('TwoFactorStatusResponse', fields={
    'detail':        serializers.CharField(),
    'is_2fa_enabled': serializers.BooleanField(),
})


# ─── Auth endpoints ───────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'], summary='Register a new user',
        request=UserRegistrationSerializer,
        responses={201: _msg, 400: OpenApiResponse(description='Validation error')},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate and send OTP
        code = str(secrets.randbelow(900000) + 100000)
        cache.set(f'register_otp:{user.pk}', code, timeout=600)
        try:
            from apps.notifications.tasks import send_sendgrid_email
            send_sendgrid_email(
                to_email=user.email,
                subject='Planova - Verify your email',
                text_content=f'Your verification code: {code}\n(Valid for 10 minutes.)',
            )
        except Exception:
            pass
        
        return Response(
            {'detail': 'Registration successful. Please verify your email with the code sent.'},
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = LoginSerializer

    @extend_schema(
        tags=['Authentication'], summary='Log in',
        description='Authenticates with email+password. If 2FA enabled, otp_code is required.',
        request=LoginSerializer,
        responses={200: _auth_response, 401: OpenApiResponse(description='Invalid credentials')},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data['user']
        user = User.objects.get(id=user_data['id'])

        if user.role == User.Role.ORGANIZER and user.approval_status != User.ApprovalStatus.APPROVED:
            if user.approval_status == User.ApprovalStatus.PENDING:
                return Response({
                    'detail': 'Your account is pending approval.',
                    'approval_status': user.approval_status,
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.approval_status == User.ApprovalStatus.REJECTED:
                return Response({
                    'detail': 'Your account has been rejected.',
                    'approval_status': user.approval_status,
                    'note': user.approval_note,
                }, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.validated_data)


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = RefreshTokenSerializer

    @extend_schema(
        tags=['Authentication'], summary='Refresh access token',
        request=RefreshTokenSerializer,
        responses={200: _refresh_response, 401: OpenApiResponse(description='Token invalid or expired')},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    serializer_class = LogoutSerializer

    @extend_schema(
        tags=['Authentication'], summary='Log out',
        request=LogoutSerializer,
        responses={200: _msg, 400: OpenApiResponse(description='Invalid token')},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save()
        except Exception:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Logged out successfully.'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    @extend_schema(tags=['Authentication'], summary='Get / update my profile')
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    @extend_schema(
        tags=['Authentication'], summary='Change password',
        request=ChangePasswordSerializer,
        responses={200: _msg, 400: OpenApiResponse(description='Validation error')},
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        # Invalidate all existing tokens
        for t in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({'detail': 'Password changed successfully.'})


# ─── 2FA endpoints ────────────────────────────────────────────────────────────

class TwoFactorSetupView(APIView):
    serializer_class = TwoFactorSetupSerializer

    @extend_schema(
        tags=['Authentication'], summary='Start 2FA setup',
        request=TwoFactorSetupSerializer,
        responses={200: _2fa_setup_response, 400: OpenApiResponse(description='Wrong password')},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['password']):
            return Response({'detail': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        secret = pyotp.random_base32()
        otp_auth_url = pyotp.TOTP(secret).provisioning_uri(
            name=request.user.email, issuer_name='Planova'
        )
        return Response({'secret': secret, 'otp_auth_url': otp_auth_url, 'manual_entry_key': secret})


class TwoFactorVerifyView(APIView):
    serializer_class = TwoFactorVerifySerializer

    @extend_schema(
        tags=['Authentication'], summary='Verify and enable 2FA',
        request=TwoFactorVerifySerializer,
        responses={200: _2fa_status_response, 400: OpenApiResponse(description='Invalid OTP')},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        totp = pyotp.TOTP(serializer.validated_data['secret'])
        if not totp.verify(serializer.validated_data['otp_code'], valid_window=1):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.enable_two_factor(serializer.validated_data['secret'])
        for t in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({'detail': 'Two-factor authentication enabled.', 'is_2fa_enabled': True})


class TwoFactorDisableView(APIView):
    serializer_class = TwoFactorDisableSerializer

    @extend_schema(
        tags=['Authentication'], summary='Disable 2FA',
        request=TwoFactorDisableSerializer,
        responses={200: _2fa_status_response, 400: OpenApiResponse(description='Invalid password or OTP')},
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not request.user.check_password(serializer.validated_data['password']):
            return Response({'detail': 'Password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_2fa_enabled:
            return Response({'detail': '2FA is not enabled.'}, status=status.HTTP_400_BAD_REQUEST)
        totp = pyotp.TOTP(request.user.two_factor_secret)
        if not totp.verify(serializer.validated_data['otp_code'], valid_window=1):
            return Response({'detail': 'Invalid authentication code.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.disable_two_factor()
        for t in OutstandingToken.objects.filter(user=request.user):
            BlacklistedToken.objects.get_or_create(token=t)
        return Response({'detail': 'Two-factor authentication disabled.', 'is_2fa_enabled': False})


# ─── Email verification ───────────────────────────────────────────────────────

class RequestEmailVerificationView(APIView):
    @extend_schema(
        tags=['Authentication'], summary='Request email verification code',
        responses={200: _msg},
    )
    def post(self, request):
        user = request.user
        if user.is_email_verified:
            return Response({'detail': 'Email already verified.'})
        code = str(secrets.randbelow(900000) + 100000)
        cache.set(f'email_verify:{user.pk}', code, timeout=600)
        try:
            from apps.notifications.tasks import send_sendgrid_email
            send_sendgrid_email(
                to_email=user.email,
                subject='Planova — Verify your email',
                text_content=f'Your verification code: {code}\n(Valid for 10 minutes.)',
            )
        except Exception:
            pass
        return Response({'detail': 'Verification code sent to your email.'})


class ConfirmEmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'], summary='Confirm email verification',
        request=EmailVerifySerializer,
        responses={200: _auth_response, 400: OpenApiResponse(description='Invalid or expired code')},
    )
    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        # Try registration OTP first, then regular email verification
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid email or code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        register_code = cache.get(f'register_otp:{user.pk}')
        email_code = cache.get(f'email_verify:{user.pk}')
        
        if register_code and register_code == code:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified', 'updated_at'])
            cache.delete(f'register_otp:{user.pk}')
            
            # Set approval based on role
            if user.role == User.Role.ORGANIZER:
                user.approval_status = User.ApprovalStatus.PENDING
            else:
                user.approval_status = User.ApprovalStatus.APPROVED
            user.save(update_fields=['approval_status', 'updated_at'])
            
            return Response({
                'detail': 'Email verified successfully.',
                'approval_status': user.approval_status,
            })
        elif email_code and email_code == code:
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified', 'updated_at'])
            cache.delete(f'email_verify:{user.pk}')
            return Response({'detail': 'Email verified successfully.'})
        
        return Response({'detail': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.is_email_verified = True
        request.user.save(update_fields=['is_email_verified', 'updated_at'])
        cache.delete(f'email_verify:{request.user.pk}')
        return Response({'detail': 'Email verified successfully.'})


# ─── Password reset ───────────────────────────────────────────────────────────

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'], summary='Request password reset code',
        request=inline_serializer('PasswordResetRequest', fields={'email': serializers.EmailField()}),
        responses={200: _msg},
    )
    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'If this email exists, a reset code has been sent.'})
        code = str(secrets.randbelow(900000) + 100000)
        cache.set(f'pwd_reset:{email}', code, timeout=600)
        try:
            from apps.notifications.tasks import send_sendgrid_email
            send_sendgrid_email(
                to_email=email,
                subject='Planova — Password Reset',
                text_content=f'Your password reset code: {code}\n(Valid for 10 minutes.)',
            )
        except Exception:
            pass
        return Response({'detail': 'If this email exists, a reset code has been sent.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=['Authentication'], summary='Confirm password reset',
        request=inline_serializer('PasswordResetConfirm', fields={
            'email':        serializers.EmailField(),
            'code':         serializers.CharField(),
            'new_password': serializers.CharField(),
        }),
        responses={200: _msg, 400: OpenApiResponse(description='Invalid code or user')},
    )
    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        code     = request.data.get('code', '')
        new_pass = request.data.get('new_password', '')
        stored   = cache.get(f'pwd_reset:{email}')
        if not stored or stored != code:
            return Response({'detail': 'Invalid or expired code.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_pass)
        user.save()
        cache.delete(f'pwd_reset:{email}')
        return Response({'detail': 'Password reset successfully.'})


# ─── User approval endpoints ───────────────────────────────────────────────────

class ListPendingOrganizersView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.filter(
            role=User.Role.ORGANIZER,
            approval_status=User.ApprovalStatus.PENDING,
        ).order_by('-created_at')
        data = [{
            'id': u.id,
            'email': u.email,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'phone': u.phone,
            'created_at': u.created_at.isoformat(),
        } for u in users]
        return Response(data)


class ApproveOrganizerView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role=User.Role.ORGANIZER)
        except User.DoesNotExist:
            return Response({'detail': 'Organizer not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.approval_status = User.ApprovalStatus.APPROVED
        user.save(update_fields=['approval_status', 'updated_at'])
        return Response({'detail': 'Organizer approved.', 'approval_status': user.approval_status})


class RejectOrganizerView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, role=User.Role.ORGANIZER)
        except User.DoesNotExist:
            return Response({'detail': 'Organizer not found.'}, status=status.HTTP_404_NOT_FOUND)

        note = request.data.get('note', '')
        user.approval_status = User.ApprovalStatus.REJECTED
        user.approval_note = note
        user.save(update_fields=['approval_status', 'approval_note', 'updated_at'])
        return Response({'detail': 'Organizer rejected.', 'approval_status': user.approval_status})
