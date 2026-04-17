import pytest
from rest_framework import status
from django.core.cache import cache
from apps.accounts.models import User

@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='verify@test.com', password='Pass123!',
        first_name='V', last_name='User', role=User.Role.ATTENDEE
    )

class TestEmailVerification:
    def test_request_verification_sends_code(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.post('/api/auth/email/request-verification/')
        assert resp.status_code == status.HTTP_200_OK
        assert 'detail' in resp.data

    def test_confirm_with_valid_code(self, api_client, user):
        api_client.force_authenticate(user=user)
        cache.set(f'email_verify:{user.pk}', '123456', timeout=600)
        resp = api_client.post('/api/auth/email/confirm-verification/', {'code': '123456'}, format='json')
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_email_verified is True

    def test_confirm_with_wrong_code(self, api_client, user):
        api_client.force_authenticate(user=user)
        cache.set(f'email_verify:{user.pk}', '999999', timeout=600)
        resp = api_client.post('/api/auth/email/confirm-verification/', {'code': '000000'}, format='json')
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

class TestPasswordReset:
    def test_request_reset_always_200(self, api_client):
        resp = api_client.post('/api/auth/password-reset/', {'email': 'nonexistent@x.com'}, format='json')
        assert resp.status_code == status.HTTP_200_OK

    def test_confirm_reset_with_valid_code(self, api_client, user):
        cache.set(f'pwd_reset:{user.email}', '654321', timeout=600)
        resp = api_client.post('/api/auth/password-reset/confirm/', {
            'email': user.email, 'code': '654321', 'new_password': 'NewSecure456!'
        }, format='json')
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('NewSecure456!')
