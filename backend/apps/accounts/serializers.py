from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import pyotp
import secrets
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from .models import User


def send_verification_email(user):
    """Generate OTP code and send verification email to user."""
    code = str(secrets.randbelow(900000) + 100000)
    cache.set(f'verify_{user.pk}', code, timeout=600)

    try:
        from apps.notifications.tasks import send_sendgrid_email
        send_sendgrid_email(
            to_email=user.email,
            subject='Planova - Verify your email',
            text_content=f'Your verification code: {code}\n(Valid for 10 minutes.)',
        )
    except Exception:
        pass

    return code


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'phone']

    def validate(self, attrs):
        try:
            if attrs.get('password') != attrs.get('password_confirm'):
                raise serializers.ValidationError({'password': 'Passwords do not match.'})
            
            role = attrs.get('role')
            if role not in [User.Role.ATTENDEE, User.Role.ORGANIZER, 'attendee', 'organizer']:
                attrs['role'] = User.Role.ATTENDEE
            
            return attrs
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Registration validation error: {str(e)}")
            raise serializers.ValidationError({'detail': 'Invalid registration data.'})

    def create(self, validated_data):
        try:
            validated_data['status'] = User.Status.PENDING
            validated_data['is_active'] = False
            validated_data['role'] = validated_data.get('role') or User.Role.ATTENDEE
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Registration create error: {str(e)}")
            raise serializers.ValidationError({'detail': 'Failed to create user. Please try again.'})


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'status', 'avatar', 'phone', 'is_2fa_enabled',
                  'two_factor_enabled_at', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'status', 'is_2fa_enabled',
                          'two_factor_enabled_at', 'created_at']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password': 'Passwords do not match.'})
        return attrs


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD
    otp_code = serializers.CharField(required=False, allow_blank=False, write_only=True)

    @classmethod
    def get_token(cls, user):
        try:
            token = super().get_token(user)
            token['email'] = user.email
            token['role'] = user.role or User.Role.ATTENDEE
            token['status'] = user.status or User.Status.APPROVED
            token['is_2fa_enabled'] = user.is_2fa_enabled or False
            return token
        except Exception as e:
            # If token generation fails, still return a basic token
            token = RefreshToken.for_user(user)
            token['email'] = user.email
            token['role'] = user.role or User.Role.ATTENDEE
            token['status'] = user.status or User.Status.APPROVED
            return token

    def validate(self, attrs):
        email = attrs.get(self.username_field) or attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({'detail': 'Email and password are required.'})

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Email ou mot de passe incorrect.'})
        except Exception:
            raise serializers.ValidationError({'detail': 'Email ou mot de passe incorrect.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Email ou mot de passe incorrect.'})

        if not user.is_active:
            if user.ban_reason:
                raise serializers.ValidationError({
                    'detail': 'Votre compte a été banni. Contactez l\'administrateur.',
                    'status': 'banned'
                })
            user.is_active = True
            user.status = user.status or User.Status.APPROVED
            user.role = user.role or User.Role.ATTENDEE
            user.save(update_fields=['is_active', 'status', 'role', 'updated_at'])

        otp_code = attrs.get('otp_code')
        
        if user.is_2fa_enabled:
            if not otp_code:
                raise serializers.ValidationError({'otp_code': 'Code OTP requis pour ce compte.'})
            if not user.two_factor_secret:
                raise serializers.ValidationError({'detail': '2FA configurée mais aucun secret trouvé.'})
            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(otp_code, valid_window=1):
                raise serializers.ValidationError({'otp_code': 'Code OTP invalide.'})

        refresh = self.get_token(user)

        return {
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if 'refresh' not in data:
            data['refresh'] = attrs['refresh']

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        refresh_token = self.validated_data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()

        return refresh_token


class TwoFactorSetupSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)


class TwoFactorVerifySerializer(serializers.Serializer):
    secret = serializers.CharField()
    otp_code = serializers.CharField()

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('OTP code must contain only digits.')
        return value


class TwoFactorDisableSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(write_only=True)

    def validate_otp_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('OTP code must contain only digits.')
        return value
