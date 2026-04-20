import pyotp
import pytest
from apps.accounts.models import User


@pytest.mark.django_db
def test_register_endpoint_creates_user_and_returns_tokens(api_client):
    response = api_client.post(
        '/api/auth/register/',
        {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'role': 'attendee',
            'phone': '1234567890',
        },
        format='json',
    )

    assert response.status_code == 201
    assert response.data['user']['email'] == 'newuser@example.com'
    assert 'access' in response.data['tokens']
    assert 'refresh' in response.data['tokens']


@pytest.mark.django_db
def test_login_requires_otp_when_two_factor_enabled(api_client, user_factory):
    user = user_factory(email='twofa@example.com', password='StrongPass123!')
    secret = pyotp.random_base32()
    user.enable_two_factor(secret)

    no_otp_response = api_client.post(
        '/api/auth/login/',
        {'email': user.email, 'password': 'StrongPass123!'},
        format='json',
    )

    assert no_otp_response.status_code == 400
    assert 'otp_code' in no_otp_response.data

    valid_otp = pyotp.TOTP(secret).now()
    otp_response = api_client.post(
        '/api/auth/login/',
        {'email': user.email, 'password': 'StrongPass123!', 'otp_code': valid_otp},
        format='json',
    )

    assert otp_response.status_code == 200
    assert otp_response.data['user']['is_2fa_enabled'] is True
    assert 'access' in otp_response.data['tokens']


@pytest.mark.django_db
def test_two_factor_setup_verify_disable_flow(api_client, user_factory, auth_headers_for):
    user = user_factory(password='StrongPass123!')
    api_client.credentials(**auth_headers_for(user))

    setup_response = api_client.post(
        '/api/auth/2fa/setup/',
        {'password': 'StrongPass123!'},
        format='json',
    )

    assert setup_response.status_code == 200
    assert setup_response.data['secret']
    assert 'otpauth://' in setup_response.data['otp_auth_url']

    secret = setup_response.data['secret']
    verify_response = api_client.post(
        '/api/auth/2fa/verify/',
        {'secret': secret, 'otp_code': pyotp.TOTP(secret).now()},
        format='json',
    )

    assert verify_response.status_code == 200
    assert verify_response.data['is_2fa_enabled'] is True

    user.refresh_from_db()
    assert user.is_2fa_enabled is True

    disable_response = api_client.post(
        '/api/auth/2fa/disable/',
        {'password': 'StrongPass123!', 'otp_code': pyotp.TOTP(secret).now()},
        format='json',
    )

    assert disable_response.status_code == 200
    assert disable_response.data['is_2fa_enabled'] is False


@pytest.mark.django_db
def test_default_accounts_exist_and_login(api_client):
    admin = User.objects.get(email='admin@planova.com')
    organizer = User.objects.get(email='organisateur@planova.com')
    attendee = User.objects.get(email='user@planova.com')

    assert admin.role == User.Role.ADMIN
    assert organizer.role == User.Role.ORGANIZER
    assert attendee.role == User.Role.ATTENDEE
    assert admin.check_password('admin123')
    assert organizer.check_password('org123')
    assert attendee.check_password('user123')

    response = api_client.post(
        '/api/auth/login/',
        {'email': 'admin@planova.com', 'password': 'admin123'},
        format='json',
    )

    assert response.status_code == 200
    assert response.data['user']['role'] == 'admin'
