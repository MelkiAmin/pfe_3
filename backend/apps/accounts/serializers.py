from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import pyotp
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'role', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name',
                  'role', 'avatar', 'phone', 'is_email_verified', 'is_2fa_enabled',
                  'two_factor_enabled_at', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'is_email_verified', 'is_2fa_enabled',
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
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['is_2fa_enabled'] = user.is_2fa_enabled
        return token

    def validate(self, attrs):
        email = attrs.get(self.username_field) or attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({'detail': 'Email and password are required.'})

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})

        if not user.is_active:
            raise serializers.ValidationError({'detail': 'User account is disabled.'})

        self.user = user
        otp_code = attrs.get('otp_code')

        if user.is_2fa_enabled:
            if not otp_code:
                raise serializers.ValidationError({'otp_code': 'OTP code is required for this account.'})

            if not user.two_factor_secret:
                raise serializers.ValidationError({'detail': '2FA is configured but no secret found.'})

            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(otp_code, valid_window=1):
                raise serializers.ValidationError({'otp_code': 'Invalid authentication code.'})

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
